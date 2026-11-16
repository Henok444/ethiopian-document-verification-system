import json
import streamlit as st

SUPPORTED_DEFAULT_FIELDS = ["name", "id", "birth_date", "expiry_date"]


def render_rule_builder() -> dict:
    """Renders the configuration and rule creation UI, returning the validated request payload."""
    st.subheader("1. Document Configuration")
    document_type = st.text_input(
        "Document Type",
        value="identity_card",
        placeholder="e.g. identity_card, passport",
        help="Type identifier for the document family being processed.",
    )

    st.subheader("2. Fields to Extract")
    st.caption("Select standard fields to extract from the Ethiopian ID card.")

    selected_defaults = st.multiselect(
        "Standard Extraction Fields",
        options=SUPPORTED_DEFAULT_FIELDS,
        default=SUPPORTED_DEFAULT_FIELDS,
        help="Predefined extractor models available in the system.",
    )

    st.divider()

    st.subheader("3. Verification Rules")
    st.caption("Define validation criteria to check against the extracted fields.")

    col_r_num, _ = st.columns([1, 2])
    with col_r_num:
        number_of_rules = st.number_input(
            "Number of rules", min_value=1, max_value=20, value=len(selected_defaults), step=1
        )

    rules = []
    default_rules = [
        {"name": f"{field}_required", "field": field, "check": "exist"}
        for field in selected_defaults
    ]

    for idx in range(int(number_of_rules)):
        default_rule = default_rules[idx] if idx < len(default_rules) else {}
        st.markdown(f"**Rule {idx + 1}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            r_name = st.text_input(
                "Rule name",
                value=default_rule.get("name", f"rule_{idx + 1}"),
                key=f"rule_name_{idx}",
                placeholder="e.g. name_required",
            )
        with c2:
            r_field = st.text_input(
                "Target Field",
                value=default_rule.get("field", selected_defaults[idx] if idx < len(selected_defaults) else "name"),
                key=f"rule_field_{idx}",
                placeholder="e.g. name, id",
            )
        with c3:
            check_opts = ["exist", "pattern", "exact_match", "comparison"]
            default_check = default_rule.get("check", "exist")
            check_idx = check_opts.index(default_check) if default_check in check_opts else 0
            r_check = st.selectbox(
                "Check Type",
                options=check_opts,
                index=check_idx,
                key=f"check_type_{idx}",
            )

        if r_name.strip() and r_field.strip():
            rules.append({
                "name": r_name.strip(),
                "field": r_field.strip(),
                "check": r_check,
            })

    request_data = {
        "document_type": document_type.strip(),
        "extract": {
            "default": selected_defaults,
            "custom_keyword": [],
            "key_and_pattern": {},
        },
        "rules": rules,
        "output": {"name": "default", "region": "all"},
    }

    st.divider()

    # Option to upload an existing JSON configuration file instead
    with st.expander("📁 Or upload an existing JSON configuration file"):
        uploaded_json = st.file_uploader(
            "Upload JSON configuration", type=["json"], key="json_cfg_uploader"
        )
        if uploaded_json is not None:
            try:
                request_data = json.load(uploaded_json)
                st.success("Custom JSON configuration loaded successfully.")
            except Exception as e:
                st.error(f"Failed to parse JSON file: {e}")

    with st.expander("👁️ Preview Configuration JSON"):
        st.json(request_data)
        st.download_button(
            label="Download Configuration JSON",
            data=json.dumps(request_data, indent=2),
            file_name="verification_request.json",
            mime="application/json",
        )

    return request_data
