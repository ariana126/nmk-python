Feature: Vitals Alerting
  As a clinic member
  I want to see a patient's out-of-range vitals
  So that I can quickly identify and respond to emergencies

  Background:
    Given the application is running
    And I am logged in as a clinic member
    And a patient exists with ID "patient-id"

  Scenario: Vitals with out-of-range heart rate
    When I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | 120  |
      | systolicBp         | 130  |
      | temperature        | 36.5 |
    And I open the patient's alerting vitals page
    Then the response status should be 200
    And I should see a vitals record at the top with the following details:
      | heartRatePerMinute | 120             |
      | systolicBp         | 130             |
      | temperature        | 36.5            |
      | recordedAt         | <past-datetime> |

  Scenario: Vitals with out-of-range systolic blood pressure
    When I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | 100  |
      | systolicBp         | 160  |
      | temperature        | 36.5 |
    And I open the patient's alerting vitals page
    Then the response status should be 200
    And I should see a vitals record at the top with the following details:
      | heartRatePerMinute | 100             |
      | systolicBp         | 160             |
      | temperature        | 36.5            |
      | recordedAt         | <past-datetime> |

  Scenario: Vitals with out-of-range temperature
    When I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | 100  |
      | systolicBp         | 130  |
      | temperature        | 34.5 |
    And I open the patient's alerting vitals page
    Then the response status should be 200
    And I should see a vitals record at the top with the following details:
      | heartRatePerMinute | 100             |
      | systolicBp         | 130             |
      | temperature        | 34.5            |
      | recordedAt         | <past-datetime> |

  Scenario: Normal vitals
    When I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | 100  |
      | systolicBp         | 130  |
      | temperature        | 36.5 |
    And I open the patient's alerting vitals page
    Then the response status should be 200
    And the vitals list should be empty