import re

from src.document_verification.schemas import (
    VerificationRequest,
    VerificationResult,
    RuleResult,
)


def verify(request: VerificationRequest) -> VerificationResult:
    results = []

    for rule in request.rules:
        field_name = rule["field"]
        check = rule["check"]
        field = request.fields.get(field_name)


        
        if field is not None and field.confidence is not None and  field.confidence < 0.8:
            results.append(RuleResult(
                rule_name= rule["name"] , 
                status= "needs_review" , 
                message= f"condfidence level is low needs human review"
            ))
            continue



        if check == "required":
            if field is None or not field.value or not field.value.strip():
                results.append(
                    RuleResult(
                        rule_name=rule["name"],
                        status="failed",
                        message=f"{field_name} is required.",
                    )
                )
            else:
                results.append(
                    RuleResult(
                        rule_name=rule["name"],
                        status="passed",
                        message=f"{field_name} is present.",
                    )
                )

        elif check == "pattern":
            pattern = rule["pattern"]

            if field is None or not field.value:
                print("1")
                results.append(
                    RuleResult(
                        rule_name=rule["name"],
                        status="failed",
                        message=f"{field_name} is missing.",
                    )
                )
            elif re.fullmatch(pattern, field.value):
                results.append(
                    RuleResult(
                        rule_name=rule["name"],
                        status="passed",
                        message=f"{field_name} has a valid format.",
                    )
                )
                print("2")
            else:
                results.append(
                    RuleResult(
                        rule_name=rule["name"],
                        status="failed",
                        message=f"{field_name} has an invalid format.",
                    )
                )
        else:
            results.append(
                RuleResult(
                    rule_name=rule["name"],
                    status="needs_review",
                    message=f"Unsupported rule type: {check}",
                )
            )
            print("3")

    if any(result.status == "failed" for result in results) or results == [] or len(results) != len(request.rules): #===============>> verify if the sent file is valid or does it just jump 
        overall_status = "failed"
    elif any(result.status == "needs_review" for result in results):
        overall_status = "needs_review"
    else:
        overall_status = "passed"

    return VerificationResult(
        status=overall_status,
        rule_results=results,
    )
