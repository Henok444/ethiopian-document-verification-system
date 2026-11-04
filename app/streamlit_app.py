import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Document Verification System",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Document Verification System")
st.caption("Document verification and batch processing")

# -------------------------
# Select verification mode
# -------------------------

mode = st.radio(
    "Verification mode",
    ["Single Document", "Batch Verification"],
    horizontal=True
)

st.divider()

# -------------------------
# Upload request file
# -------------------------

st.subheader("Verification Rules")

json_file = st.file_uploader(
    "Upload JSON request file",
    type=["json"],
    key="json_file"
)

# -------------------------
# Single document mode
# -------------------------

if mode == "Single Document":

    st.subheader("Upload Document")

    image_file = st.file_uploader(
        "Upload identity document",
        type=["jpg", "jpeg", "png"],
        key="single_image"
    )

    if st.button("Verify Document", type="primary"):

        if json_file is None or image_file is None:
            st.warning("Please upload both files.")

        else:
            files = {
                "json_file": (
                    json_file.name,
                    json_file.getvalue(),
                    "application/json"
                ),
                "image_file": (
                    image_file.name,
                    image_file.getvalue(),
                    image_file.type
                )
            }

            try:
                with st.spinner("Verifying document..."):

                    response = requests.post(
                        f"{API_URL}/verify",
                        files=files,
                        timeout=120
                    )

                    response.raise_for_status()
                    result = response.json()

                st.session_state["single_result"] = result

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the API.")

            except requests.exceptions.Timeout:
                st.error("The request timed out.")

            except requests.exceptions.HTTPError:
                st.error(f"API error: {response.status_code}")
                st.write(response.text)

            except ValueError:
                st.error("Invalid JSON response from API.")

# -------------------------
# Batch verification mode
# -------------------------

else:

    st.subheader("Upload Multiple Documents")

    image_files = st.file_uploader(
        "Upload identity documents",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="batch_images"
    )

    if st.button("Verify All Documents", type="primary"):

        if json_file is None or not image_files:
            st.warning("Please upload a JSON file and at least one image.")

        else:

            files = [
                (
                    "json_file",
                    (
                        json_file.name,
                        json_file.getvalue(),
                        "application/json"
                    )
                )
            ]

            files.extend(
                [
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
            )

            try:
                with st.spinner(
                    f"Verifying {len(image_files)} documents..."
                ):

                    response = requests.post(
                        f"{API_URL}/verify_batch",
                        files=files,
                        timeout=300
                    )

                    response.raise_for_status()
                    result = response.json()

                st.session_state["batch_result"] = result

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the API.")

            except requests.exceptions.Timeout:
                st.error("The batch request timed out.")

            except requests.exceptions.HTTPError:
                st.error(f"API error: {response.status_code}")
                st.write(response.text)

            except ValueError:
                st.error("Invalid JSON response from API.")

# -------------------------
# Result display functions
# -------------------------

def display_document_result(result):

    if "error" in result:
        st.error(f"Processing error: {result['error']}")
        return

    status = result.get("status", "unknown").lower()

    if status == "passed":
        st.success("✓ DOCUMENT PASSED")

    elif status == "failed":
        st.error("✗ DOCUMENT FAILED")

    elif status == "needs_review":
        st.warning("⚠ HUMAN REVIEW REQUIRED")

    else:
        st.info(f"Status: {status.upper()}")

    rule_results = result.get("rule_results", [])

    passed = sum(
        rule.get("status") == "passed"
        for rule in rule_results
    )

    failed = sum(
        rule.get("status") == "failed"
        for rule in rule_results
    )

    review = sum(
        rule.get("status") == "needs_review"
        for rule in rule_results
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Passed", passed)
    col2.metric("Failed", failed)
    col3.metric("Needs Review", review)

    st.markdown("#### Individual Rule Results")

    for rule in rule_results:

        name = rule.get("rule_name", "Unknown rule")
        status = rule.get("status", "unknown").lower()
        message = rule.get("message", "No message provided.")

        if status == "passed":
            icon = "✅"
        elif status == "failed":
            icon = "❌"
        elif status == "needs_review":
            icon = "⚠️"
        else:
            icon = "❔"

        with st.expander(f"{icon} {name}"):
            st.write(f"**Status:** {status.upper()}")
            st.write(f"**Message:** {message}")


# -------------------------
# Display single result
# -------------------------

if mode == "Single Document" and "single_result" in st.session_state:

    st.divider()
    st.header("Verification Result")

    display_document_result(
        st.session_state["single_result"]
    )

    with st.expander("Raw API response"):
        st.json(st.session_state["single_result"])


# -------------------------
# Display batch results
# -------------------------

if mode == "Batch Verification" and "batch_result" in st.session_state:

    result = st.session_state["batch_result"]

    st.divider()
    st.header("Batch Verification Results")

    documents = result.get("results", [])

    total = result.get("total_documents", len(documents))

    processed = sum(
        "result" in document for document in documents
    )

    errors = total - processed

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Documents", total)
    col2.metric("Processed", processed)
    col3.metric("Processing Errors", errors)

    st.divider()

    for index, document in enumerate(documents, start=1):

        filename = document.get(
            "filename",
            f"Document {index}"
        )

        with st.expander(f"📄 {index}. {filename}"):

            if "error" in document:
                st.error(document["error"])

            else:
                display_document_result(
                    document["result"]
                )

    with st.expander("Raw batch API response"):
        st.json(result)