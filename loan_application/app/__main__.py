def main():
    from loan_application.app import app
    from loan_application.external_services.credit_bureaus.extrafax.sandbox.fetcher import fixture_repo
    fixture_repo.load_fixtures()
    app.app.run(port=8001)


if __name__ == '__main__':
    main()
