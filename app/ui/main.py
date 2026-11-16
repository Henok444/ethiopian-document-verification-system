import sys
from pathlib import Path

# Ensure project root is in sys.path so 'app' and 'src' packages can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.ui.components.rule_builder import render_rule_builder
from app.ui.components.result_card import render_document_result, render_batch_results
from app.ui.services.api_client import VerificationAPIClient, APIClientError

st.set_page_config(
    page_title="Ethiopian Document Verification",
    page_icon="🇪🇹",
    layout="wide",
)

st.title("🇪🇹 Ethiopian Document Verification System")
st.caption("Verify Ethiopian national IDs and identity documents using OCR and configurable rules.")

client = VerificationAPIClient()

# Mode selection
mode = st.radio(
    "Verification Mode",
    options=["Single Document", "Batch Verification"],
    horizontal=True,
)

st.divider()

# Step 1 & 2: Build or Load Rules
config_data = render_rule_builder()

st.divider()

# Step 3: Upload and Run Verification
if mode == "Single Document":
    st.subheader("4. Upload & Verify Document")
    image_file = st.file_uploader(
        "Upload identity document image",
        type=["png", "jpg", "jpeg"],
        key="single_image_uploader",
    )

    if st.button("Verify Document", type="primary"):
        if not image_file:
            st.error("Please upload an image file before verifying.")
        elif not config_data.get("document_type"):
            st.error("Document type is required in the configuration.")
        else:
            with st.spinner("Processing OCR extraction and checking rules..."):
                try:
                    result = client.verify_single(
                        config_dict=config_data,
                        image_name=image_file.name,
                        image_bytes=image_file.getvalue(),
                        image_type=image_file.type,
                    )
                    st.session_state["single_result"] = result
                    st.session_state["single_image_bytes"] = image_file.getvalue()
                except APIClientError as err:
                    st.error(str(err))

    if "single_result" in st.session_state:
        st.divider()
        st.subheader("Verification Results")
        render_document_result(
            st.session_state["single_result"],
            image_bytes=st.session_state.get("single_image_bytes"),
        )

else:
    st.subheader("4. Upload & Verify Multiple Documents (Batch)")
    image_files = st.file_uploader(
        "Upload multiple document images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="batch_image_uploader",
    )

    if st.button("Verify All Documents", type="primary"):
        if not image_files:
            st.error("Please upload at least one image file before verifying.")
        elif not config_data.get("document_type"):
            st.error("Document type is required in the configuration.")
        else:
            with st.spinner(f"Verifying {len(image_files)} documents in batch..."):
                try:
                    batch_res = client.verify_batch(
                        config_dict=config_data,
                        image_files=image_files,
                    )
                    st.session_state["batch_result"] = batch_res
                    st.session_state["batch_files"] = image_files
                except APIClientError as err:
                    st.error(str(err))

    if "batch_result" in st.session_state:
        st.divider()
        render_batch_results(
            st.session_state["batch_result"],
            image_files=st.session_state.get("batch_files", []),
        )
