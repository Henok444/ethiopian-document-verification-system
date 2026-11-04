def output(result):
    output_result = {
        "status": result.status,
        "rule_results": [
            {
                "rule_name": rule_result.rule_name,
                "status": rule_result.status,
                "message": rule_result.message,
            }
            for rule_result in result.rule_results
        ],
    }
    return output_result