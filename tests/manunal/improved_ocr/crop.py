from document_verification_engine.image_extracter_model.improved_ocr_model.crop import crop
from pathlib import Path



base = Path(__file__).resolve



            status=result.status,
            status=getattr(result, "status", "unknown"),
            rule_results=[
                RuleResultResponse(
                    rule_name=r.rule_name,
                    status=r.status,
                    message=r.message,
                    rule_name=getattr(r, "rule_name", getattr(r, "name", "unknown")),
                    status=getattr(r, "status", "unknown"),
                    message=getattr(r, "message", ""),
                    found=getattr(r, "found", None),
                )
                for r in result.rule_results
                for r in getattr(result, "rule_results", [])
            ],
        )