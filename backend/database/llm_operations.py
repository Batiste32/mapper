from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.inspection import inspect
import re

import backend.database.models as base_model
from backend.utils.ai_engine import call_ollama
from backend.utils.constants import PARSING_PROMPT

def chunk_list(data, size) :
    return [data[i:i+size] for i in range(0, len(data), size)]

def extract_field(session: Session, field: str, table_name: str) -> list[str] :
    """
    Extracts a list of values from a specific field of the chosen table.
    
    Args :
        session : SQLAlchemy session.
        field : Field name to extract values from.
    
    Returns :
        List of field values as strings.
    """
    table = getattr(base_model, table_name, None)
    if table is None :
        raise ValueError(f"Model '{table_name}' not found in provided model.")
    if field not in inspect(table).columns :
        raise ValueError(f"Field '{field}' not found in model '{table_name}'.")
    column = getattr(table, field)
    results = session.scalars(select(column)).all()
    return [str(r) if r is not None else "" for r in results]

def llm_normalize_field(session: Session, table_name: str, field: str, valid_values: list[str], model: str = "llama3", batch_size=16) -> list[str]:
    """
    USE CACHED FUNCTION llm_normalize_field_cached INSTEAD FOR EFFICIENCY.

    Call local Ollama model to enforce values in specified field corresponding to valid_values.
    Skips LLM processing for values that already match valid ones (case-insensitive).

    Args:
        session : SQLAlchemy session.
        table_name : Name of the table to look into.
        field : Field name to extract values from.
        valid_values : List of valid string values.
        model : Ollama model to call.
        batch_size : Number of values to process in the same call.

    Returns:
        List of cleaned string values.
    """
    extracted_values = extract_field(session, field, table_name)
    
    # Normalize valid values to lowercase for comparison
    valid_lower = {v.lower(): v for v in valid_values}

    preprocessed = []
    to_process = []
    process_indices = []

    # Precheck and separate values that need processing
    for i, val in enumerate(extracted_values):
        val_stripped = val.strip()
        lower_val = val_stripped.lower()
        if lower_val in valid_lower:
            # Already valid, use canonical form
            preprocessed.append(valid_lower[lower_val])
        else:
            # Needs LLM normalization
            preprocessed.append(None)
            to_process.append(val_stripped)
            process_indices.append(i)

    chunks = chunk_list(to_process, batch_size)

    for i, chunk in enumerate(chunks):
        prompt = (
            PARSING_PROMPT +
            f"Data to classify: {'; '.join(chunk)}\nValid values: {', '.join(valid_values)}"
        )
        print(f"[Batch {i+1}/{len(chunks)}] Sending {len(chunk)} entries to LLM...")
        response = call_ollama(prompt, model)
        cleaned = [x.strip() for x in response.split(';')]

        if len(cleaned) != len(chunk):
            print(f"[WARNING] Mismatch in chunk size vs cleaned output at batch {i+1}\n"
                  f"Cleaned : {cleaned} // Original : {chunk}\nKeeping original batch.")
            cleaned = chunk

        # Insert cleaned results into the correct positions
        for j, index in enumerate(process_indices[i * batch_size : i * batch_size + len(chunk)]):
            preprocessed[index] = cleaned[j]

    return preprocessed

def llm_normalize_field_cached( session: Session, table_name: str, field: str, valid_values: list[str],
    convert_dict: dict[str, str] = {}, model: str = "llama3", batch_size: int = 16 ) -> list[str]:
    """
    Normalize field values using valid values. Avoids unnecessary LLM calls
    by using a persistent convert_dict to map previously normalized values.

    Args:
        session: SQLAlchemy session.
        table_name: Name of the SQLAlchemy model.
        field: Column name to normalize.
        valid_values: List of canonical valid strings.
        convert_dict: Dict storing known mappings {incorrect_value: correct_value}.
        model: LLM model name.
        batch_size: Number of entries per LLM batch.

    Returns:
        List of normalized string values (aligned with extracted field values).
    """
    extracted_values = extract_field(session, field, table_name)

    valid_set = {v.lower(): v for v in valid_values}
    results = [None] * len(extracted_values)

    pending_batch = []
    pending_indices = []

    i = 0
    while i < len(extracted_values):
        val = extracted_values[i]
        val_stripped = val.strip()
        val_cleaned = re.sub(r'\s+', ' ', val_stripped).strip()
        val_lower = val_cleaned.lower()

        # Case 1: Already valid
        if val_lower in valid_set:
            results[i] = valid_set[val_lower]
        # Case 2: Already cached
        elif val_stripped in convert_dict:
            results[i] = convert_dict[val_stripped]
        # Case 3: Needs processing
        else:
            pending_batch.append(val_stripped)
            pending_indices.append(i)

            if len(pending_batch) >= batch_size:
                # Send batch to LLM
                print(f"[Batch] Sending {len(pending_batch)} entries to LLM, {len(extracted_values)-i} remaining to process...")
                prompt = (
                    PARSING_PROMPT +
                    f"Data to classify ({len(pending_batch)} entries): {'; '.join(pending_batch)}\nValid values: {', '.join(valid_values)}"
                )
                response = call_ollama(prompt, model)
                cleaned = [x.strip() for x in response.split(';')]

                if len(cleaned) != len(pending_batch):
                    print(f"[WARNING] Output mismatch, falling back to original values.\nOriginal : {pending_batch}\nLLM : {response}\nCleaned : {cleaned}")
                    cleaned = pending_batch

                # Store results & update cache
                for j, idx in enumerate(pending_indices):
                    convert_dict[pending_batch[j]] = cleaned[j]
                    results[idx] = cleaned[j]

                # Reset batch
                pending_batch = []
                pending_indices = []
        i += 1

    # Handle final small batch
    if pending_batch:
        print(f"[Final Batch] Sending {len(pending_batch)} entries to LLM...")
        prompt = (
            PARSING_PROMPT +
            f"Data to classify: {'; '.join(pending_batch)}\nValid values: {', '.join(valid_values)}"
        )
        response = call_ollama(prompt, model)
        cleaned = [x.strip() for x in response.split(';')]

        if len(cleaned) != len(pending_batch):
            print(f"[WARNING] Output mismatch, falling back to original values.")
            cleaned = pending_batch

        for j, idx in enumerate(pending_indices):
            convert_dict[pending_batch[j]] = cleaned[j]
            results[idx] = cleaned[j]

    return results

def update_database_nationalities(session: Session, cleaned_values: list[str]):
    profiles = session.scalars(select(base_model.Profile)).all()
    for profile, new_origin in zip(profiles, cleaned_values):
        profile.origin = new_origin
    session.commit()