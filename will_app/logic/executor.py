from helpers.formatters import format_date

def process_executor_data(form_data):
    """
    Process executor information
    """
    context = {
        "executor_name_one": form_data.get('exec1_name', ''),
        "executor_dob_one": format_date(form_data.get('exec1_dob', '')),
        "relation_executor_one": form_data.get('exec1_relation', ''),
        "include_second_executor": form_data.get('include_second_executor') in ['true', 'True', '1', True]
    }
    
    if context["include_second_executor"]:
        context.update({
            "executor_name_second": form_data.get('exec2_name', ''),
            "executor_dob_second": format_date(form_data.get('exec2_dob', '')),
            "relation_executor_second": form_data.get('exec2_relation', '')
        })
    
    # Wassiyat
    if form_data.get('wassiyat_include') in ['true', 'True', '1', True]:
        context["wassiyat_percentage_placeholder"] = form_data.get('wassiyat_percentage', '')
    
    # Specific gift
    if form_data.get('specific_gift_include') in ['true', 'True', '1', True]:
        context["specific_gift"] = form_data.get('specific_gift_text', '')
    
    return context