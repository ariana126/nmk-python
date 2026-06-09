Feature: Patient Registration
  As a clinic member
  I want to register new patients
  So that I can have records of their data

  Background:
    Given the application is running
    And I am logged in as a clinic member

  Scenario: Successful patient registration
    When I register a patient with the following details:
      | name        | Ariana Maghsoudi |
      | dateOfBirth | 2004-01-26       |
      | email       | test@example.com |
    Then the response status should be 200
    And the response body should contain the patient ID
    And I should see the patient profile with the following details:
      | name        | Ariana Maghsoudi |
      | dateOfBirth | 2004-01-26       |
      | email       | test@example.com |

  Scenario: Registration with an email already in use
    Given a patient with email "test@example.com" already exists
    When I register a patient with the following details:
      | name        | Another Patient  |
      | dateOfBirth | 1985-03-22       |
      | email       | test@example.com |
    Then the response status should be 409
    And the response should be a valid problem detail
    And the response body should contain an error indicating the patient email is taken

  Scenario: Registration with missing required fields
    When I register a patient with the following details:
      | name | Ariana Maghsoudi |
    Then the response status should be 400
    And the response should be a valid problem detail
    And the response body should contain validation errors for:
      | dateOfBirth |
      | email       |

  Scenario: Registration with an invalid email format
    When I register a patient with the following details:
      | name        | Ariana Maghsoudi |
      | dateOfBirth | 2004-01-26       |
      | email       | not-an-email     |
    Then the response status should be 400
    And the response should be a valid problem detail
    And the response body should contain validation errors for:
      | email |

  Scenario: Registration with an invalid date of birth format
    When I register a patient with the following details:
      | name        | Ariana Maghsoudi |
      | dateOfBirth | 26/01/2004       |
      | email       | test@example.com |
    Then the response status should be 400
    And the response should be a valid problem detail
    And the response body should contain validation errors for:
      | dateOfBirth |

  Scenario: Unauthenticated access is rejected
    When I log out of my account
    And I register a patient with the following details:
      | name        | Ariana Maghsoudi |
      | dateOfBirth | 2004-01-26       |
      | email       | test@example.com |
    Then the response status should be 401
    And the response should be a valid problem detail
