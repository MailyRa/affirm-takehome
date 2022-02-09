from loan_application.models.requests import Address


def resolve_minimum_age(
        address: Address
) -> int:
    """
    Resolves the minimum eligible age for users to take out loans in the
    customer's jurisdiction.
    :param address: Address
    :return:
    """
    assert address.country_code == 'US', "Only support US addresses for now"

    # By Alabama law, users must be at least 19 to be eligible for credit
    if address.region1_code == 'AL':
        return 19
    else:
        # Default to US law, where users 18 or older are eligible for credit
        return 18
