# Intern attendance register (Flask on Azure Functions)

Local demo (SQLite, no Azure needed):
    pip install flask
    flask --app app:create_app run

Local with Functions host:  pip install -r requirements.txt; cp local.settings.json.example local.settings.json; func start

Azure SQL: run schema_azure_sql.sql, add your own managers/interns, set SQL_CONNECTION_STRING in the Function App's Application Settings.
Auth: enable Entra ID authentication on the Function App; the app reads X-MS-CLIENT-PRINCIPAL-NAME.
