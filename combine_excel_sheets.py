import pandas as pd

# Read each Excel file
automation_status = pd.read_excel('automation_status.xlsx')
em_scores = pd.read_excel('em_scores.xlsx')
qa_scores = pd.read_excel('qa_scores.xlsx')
kudo_data = pd.read_excel('kudo_data.xlsx')
qa_data_template = pd.read_excel('qa_data_template.xlsx')

# Write to a single Excel file with multiple sheets
with pd.ExcelWriter('dashboard_data.xlsx') as writer:
    automation_status.to_excel(writer, sheet_name='Automation Status', index=False)
    em_scores.to_excel(writer, sheet_name='EM Scores', index=False)
    qa_scores.to_excel(writer, sheet_name='QA Scores', index=False)
    kudo_data.to_excel(writer, sheet_name='Kudo Data', index=False)
    qa_data_template.to_excel(writer, sheet_name='QA Data', index=False)

print('Combined data written to dashboard_data.xlsx') 