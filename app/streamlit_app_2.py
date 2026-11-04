import json
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Document Verification Engine",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Document Verification Engine")
st.write("Configure extraction fields and verification rules, then upload your documents.")

# --------------------------------------------------
# 1. Document configuration
# --------------------------------------------------

st.header("1. Document Configuration")

document_type = st.text_input(
    "Document type",
    value="id_card",
    placeholder="e.g. id_card"
)

# --------------------------------------------------
# 2. Fields to extract
# --------------------------------------------------

st.header("2. Fields to Extract")

st.caption("Enter the information you want the engine to extract from each document.")

number_of_fields = st.number_input(
    "Number of fields",
    min_value=1,
    max_value=50,
    value=3,
    step=1
)

extraction_fields = []

for index in range(int(number_of_fields)):
    field_name = st.text_input(
        f"Field {index + 1}",
        key=f"extract_field_{index}",
        placeholder="e.g. full_name"
    )

    if field_name.strip():
        extraction_fields.append(field_name.strip())

st.divider()

# --------------------------------------------------
# 3. Verification rules
# --------------------------------------------------

st.header("3. Verification Rules")

number_of_rules = st.number_input(
    "Number of verification rules",
    min_value=1,
    max_value=50,
    value=3,
    step=1
)

rules = []

for index in range(int(number_of_rules)):
    st.subheader(f"Rule {index + 1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        rule_name = st.text_input(
            "Rule name",
            key=f"rule_name_{index}",
            placeholder="e.g. full_name_required"
        )

    with col2:
        rule_field = st.text_input(
            "Field",
            key=f"rule_field_{index}",
            placeholder="e.g. full_name"
        )

    with col3:
        check_type = st.selectbox(
            "Check type",
            options=["required", "pattern"],
            key=f"check_type_{index}"
        )

    if rule_name.strip() and rule_field.strip():
        rules.append({
            "name": rule_name.strip(),
            "field": rule_field.strip(),
            "check": check_type
        })

    st.divider()

# --------------------------------------------------
# 4. Build JSON request
# --------------------------------------------------

request_data = {
    "document_type": document_type.strip(),
    "extract_fields": extraction_fields,
    "rules": rules
}

st.header("4. Request JSON")

st.json(request_data)

st.download_button(
    label="Download JSON configuration",
    data=json.dumps(request_data, indent=4),
    file_name="verification_request.json",
    mime="application/json"
)

# --------------------------------------------------
# 5. Upload mode
# --------------------------------------------------

st.header("5. Upload Documents")

mode = st.radio(
    "Choose verification mode",
    options=["Single Document", "Batch Documents"],
    horizontal=True
)

json_file = st.file_uploader(
    "Upload JSON configuration (optional)",
    type=["json"],
    help="Upload a JSON file to use its configuration instead of the configuration above."
)

if json_file is not None:
    try:
        request_data = json.load(json_file)
        st.success("JSON configuration loaded.")
        st.json(request_data)
    except json.JSONDecodeError:
        st.error("Invalid JSON file.")
        st.stop()

# --------------------------------------------------
# 6. Display results
# --------------------------------------------------

def display_document_result(result):

    status = result.get("status", "unknown")

    if status == "passed":
        st.success(f"Status: {status.upper()}")
    elif status == "failed":
        st.error(f"Status: {status.upper()}")
    else:
        st.warning(f"Status: {status.upper()}")

    rule_results = result.get("rule_results", [])

    if rule_results:
        st.subheader("Rule Results")

        for rule in rule_results:
            rule_status = rule.get("status", "unknown")

            if rule_status == "passed":
                st.success(
                    f"✓ {rule.get('rule_name', 'Rule')}: "
                    f"{rule.get('message', '')}"
                )
            elif rule_status == "failed":
                st.error(
                    f"✗ {rule.get('rule_name', 'Rule')}: "
                    f"{rule.get('message', '')}"
                )
            else:
                st.warning(
                    f"⚠ {rule.get('rule_name', 'Rule')}: "
                    f"{rule.get('message', '')}"
                )

    with st.expander("View complete response"):
        st.json(result)


# --------------------------------------------------
# 7. Single document verification
# --------------------------------------------------

if mode == "Single Document":

    image_file = st.file_uploader(
        "Upload document image",
        type=["png", "jpg", "jpeg"]
    )

    if st.button("Verify Document", type="primary"):

        if not document_type.strip():
            st.error("Enter a document type.")
        elif not extraction_fields:
            st.error("Enter at least one extraction field.")
        elif image_file is None:
            st.error("Upload a document image.")
        else:
            try:
                files = {
                    "json_file": (
                        "request.json",
                        json.dumps(request_data),
                        "application/json"
                    ),
                    "image_file": (
                        image_file.name,
                        image_file.getvalue(),
                        image_file.type
                    )
                }

                with st.spinner("Verifying document..."):

                    response = requests.post(
                        f"{API_URL}/verify",
                        files=files,
                        timeout=300
                    )

                if response.ok:
                    st.success("Verification completed.")
                    display_document_result(response.json())
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.code(response.text)

            except requests.RequestException as error:
                st.error(f"Could not connect to API: {error}")


# --------------------------------------------------
# 8. Batch document verification
# --------------------------------------------------

else:

    image_files = st.file_uploader(
        "Upload document images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if st.button("Verify All Documents", type="primary"):

        if not document_type.strip():
            st.error("Enter a document type.")
        elif not extraction_fields:
            st.error("Enter at least one extraction field.")
        elif not image_files:
            st.error("Upload at least one document image.")
        else:
            try:
                files = [
                    (
                        "image_files",
                        (
                            image.name,
                            image.getvalue(),
                            image.type
                        )
                    )
                    for image in image_files
                ]

                files.append(
                    (
                        "json_file",
                        (
                            "request.json",
                            json.dumps(request_data),
                            "application/json"
                        )
                    )
                )

                with st.spinner(
                    f"Verifying {len(image_files)} documents..."
                ):

                    response = requests.post(
                        f"{API_URL}/verify_batch",
                        files=files,
                        timeout=600
                    )

                if response.ok:

                    data = response.json()

                    st.success("Batch verification completed.")

                    st.metric(
                        "Total Documents",
                        data.get("total_documents", len(image_files))
                    )

                    results = data.get("results", [])

                    for index, item in enumerate(results):

                        filename = item.get(
                            "filename",
                            f"Document {index + 1}"
                        )

                        with st.expander(filename):

                            if "error" in item:
                                st.error(item["error"])

                            elif "result" in item:
                                display_document_result(item["result"])

                            else:
                                st.json(item)

                    with st.expander("View complete batch response"):
                        st.json(data)

                else:
                    st.error(f"API Error: {response.status_code}")
                    st.code(response.text)

            except requests.RequestException as error:
                st.error(f"Could not connect to API: {error}")
