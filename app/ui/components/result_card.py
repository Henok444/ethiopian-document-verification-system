import streamlit as st


def render_document_result(result: dict, image_bytes: bytes | None = None):
    """Renders formatted verification results for a single document."""
    if "error" in result:
        st.error(f"Processing error: {result['error']}")
        return

    status = (result.get("status") or "unknown").lower()
    rule_results = result.get("rule_results", [])

    # Top Status Banner
    if status == "passed":
        st.success("### ✅ DOCUMENT PASSED")
    elif status == "failed":
        st.error("### ❌ DOCUMENT FAILED")
    elif status == "needs_review":
        st.warning("### ⚠️ HUMAN REVIEW REQUIRED")
    else:
        st.info(f"### Status: {status.upper()}")

    # Summary Metrics
    passed = sum(1 for r in rule_results if r.get("status") == "passed")
    failed = sum(1 for r in rule_results if r.get("status") == "failed")
    review = sum(1 for r in rule_results if r.get("status") == "needs_review")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rules Passed", passed)
    c2.metric("Rules Failed", failed)
    c3.metric("Needs Review", review)

    st.markdown("#### Rule Details")
    for r in rule_results:
        r_name = r.get("rule_name", "Rule")
        r_status = (r.get("status") or "unknown").lower()
        r_msg = r.get("message", "")
        r_found = r.get("found")

        icon = "✅" if r_status == "passed" else ("❌" if r_status == "failed" else "⚠️")

        with st.expander(f"{icon} {r_name} — {r_status.upper()}"):
            st.write(f"**Message:** {r_msg}")
            if r_found is not None:
                st.write(f"**Found Value:** `{r_found}`")

    # Document Image Preview (if available)
    if image_bytes is not None:
        with st.expander("Inspected Document Image", expanded=True):
            st.image(image_bytes, caption="Uploaded Document", use_container_width=True)


def render_batch_results(batch_data: dict, image_files: list):
    """Renders formatted verification results for a batch of documents."""
    total = batch_data.get("total_documents", len(image_files))
    results = batch_data.get("results", [])

    successful = sum(1 for item in results if item.get("result") and item["result"].get("status") == "passed")
    failed = sum(1 for item in results if item.get("result") and item["result"].get("status") == "failed")
    review = sum(1 for item in results if item.get("result") and item["result"].get("status") == "needs_review")
    errors = sum(1 for item in results if "error" in item and item["error"])

    st.markdown("### Batch Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Documents", total)
    c2.metric("Passed", successful)
    c3.metric("Failed", failed)
    c4.metric("Needs Review", review)
    c5.metric("System Errors", errors)

    st.divider()

    image_map = {img.name: img.getvalue() for img in image_files}

    for idx, item in enumerate(results, start=1):
        filename = item.get("filename", f"Document {idx}")
        doc_res = item.get("result")
        doc_err = item.get("error")

        if doc_err:
            header = f"❌ {idx}. {filename} — ERROR"
        elif doc_res:
            status = doc_res.get("status", "UNKNOWN").upper()
            icon = "✅" if status == "PASSED" else ("❌" if status == "FAILED" else "⚠️")
            header = f"{icon} {idx}. {filename} — {status}"
        else:
            header = f"📄 {idx}. {filename}"

        with st.expander(header):
            if doc_err:
                st.error(f"Error during verification: {doc_err}")
            elif doc_res:
                render_document_result(doc_res, image_bytes=image_map.get(filename))
