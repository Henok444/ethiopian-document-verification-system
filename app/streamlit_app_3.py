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
st.write("Configure extraction fields and verification rules, then verify your documents.")

# --------------------------------------------------
# 1. Document configuration
# --------------------------------------------------

st.header("1. Document Configuration")

document_type = st.text_input(
    "Document type",
    value="identity_card"
)

# --------------------------------------------------
# 2. Fields to extract
# --------------------------------------------------

st.header("2. Fields to Extract")

st.caption("Specify which fields should be extracted from the document.")

number_of_fields = st.number_input(
    "Number of fields",
    min_value=1,
    max_value=50,
    value=4,
    step=1
)

extraction_fields = []

for index in range(int(number_of_fields)):
    field_name = st.text_input(
        f"Field {index + 1}",
        key=f"extract_field_{index}",
        placeholder="e.g. name"
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
    value=4,
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
            placeholder="e.g. name_required"
        )

    with col2:
        rule_field = st.text_input(
            "Field",
            key=f"rule_field_{index}",
            placeholder="e.g. name"
        )

    with col3:
        check_type = st.selectbox(
            "Check type",
            options=[
                "exist",
                "pattern",
                "exact_match",
                "comparison"
            ],
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
# 4. Output configuration
# --------------------------------------------------

st.header("4. Output Configuration")

col1, col2 = st.columns(2)

with col1:
    output_name = st.text_input(
        "Name output",
        value="default",
        help="Output configuration for extracted names."
    )

with col2:
    output_region = st.text_input(
        "Region output",
        value="all",
        help="Output configuration for region information."
    )

# --------------------------------------------------
# 5. Build JSON request
# --------------------------------------------------

request_data = {
    "document_type": document_type.strip(),
    "extract": {
        "default": extraction_fields
    },
    "rules": rules,
    "output": {
        "name": output_name.strip(),
        "region": output_region.strip()
    }
}

# --------------------------------------------------
# 6. JSON preview and download
# --------------------------------------------------

st.header("5. Request JSON")

st.json(request_data)

st.download_button(
    label="Download JSON configuration",
    data=json.dumps(request_data, indent=4),
    file_name="verification_request.json",
    mime="application/json"
)

# --------------------------------------------------
# 7. Upload mode
# --------------------------------------------------

st.header("6. Upload Documents")

mode = st.radio(
    "Verification mode",
    options=["Single Document", "Batch Documents"],
    horizontal=True
)

json_file = st.file_uploader(
    "Upload an existing JSON configuration (optional)",
    type=["json"]
)

if json_file is not None:

    try:
        uploaded_request = json.load(json_file)

        if not isinstance(uploaded_request, dict):
            st.error("The JSON configuration must be an object.")
            st.stop()

        request_data = uploaded_request

        st.success("JSON configuration loaded successfully.")

        with st.expander("View uploaded JSON"):
            st.json(request_data)

    except json.JSONDecodeError:
        st.error("Invalid JSON configuration.")
        st.stop()

# --------------------------------------------------
# 8. Display verification results
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

            message = (
                f"{rule.get('rule_name', 'Rule')}: "
                f"{rule.get('message', '')}"
            )

            if rule_status == "passed":
                st.success(f"✓ {message}")

            elif rule_status == "failed":
                st.error(f"✗ {message}")

            else:
                st.warning(f"⚠ {message}")

    with st.expander("View complete response"):
        st.json(result)


# --------------------------------------------------
# 9. Single document verification
# --------------------------------------------------

if mode == "Single Document":

    image_file = st.file_uploader(
        "Upload document image",
        type=["png", "jpg", "jpeg"]
    )

    if st.button("Verify Document", type="primary"):

        if image_file is None:
            st.error("Please upload a document image.")

        elif not request_data.get("document_type"):
            st.error("Document type is required.")

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
# 10. Batch document verification
# --------------------------------------------------

else:

    image_files = st.file_uploader(
        "Upload document images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if st.button("Verify All Documents", type="primary"):

        if not image_files:
            st.error("Please upload at least one document image.")

        elif not request_data.get("document_type"):
            st.error("Document type is required.")

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
                        data.get(
                            "total_documents",
                            len(image_files)
                        )
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

                                display_document_result(
                                    item["result"]
                                )

                            else:

                                st.json(item)

                    with st.expander("View complete batch response"):
                        st.json(data)

                else:

                    st.error(f"API Error: {response.status_code}")
                    st.code(response.text)

            except requests.RequestException as error:

                st.error(f"Could not connect to API: {error}")

