import pytest
from assertpy.assertpy import assert_that

from framework.domain import Email
from framework.domain import InvalidEmail


def test_valid_email_address_is_accepted():
    email_address: str = 'ariana.maghsoudi82@gmail.com'

    sut = Email.from_string(email_address)

    assert_that(sut.as_string).is_equal_to(email_address)

def test_an_email_address_without_domain_is_not_valid():
    email_address: str = 'ariana.maghsoudi82@'

    with pytest.raises(InvalidEmail):
        sut = Email.from_string(email_address)

def test_an_email_address_without_the_at_sign_is_not_valid():
    email_address: str = 'ariana.maghsoudi82gmail.com'

    with pytest.raises(InvalidEmail):
        sut = Email.from_string(email_address)

def test_an_empty_email_address_is_not_valid():
    email_address: str = ''

    with pytest.raises(InvalidEmail):
        sut = Email.from_string(email_address)

def test_an_email_address_will_be_normalized_to_lowercase_characters():
    email_address: str = 'Ariana.Maghsoudi82@gmail.com'

    sut = Email.from_string(email_address)

    assert_that(sut.as_string).is_equal_to('ariana.maghsoudi82@gmail.com')