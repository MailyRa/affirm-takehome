import connexion


app = connexion.App(__name__, specification_dir='openapi/')
app.add_api('openapi.yaml', strict_validation=True, validate_responses=True)
