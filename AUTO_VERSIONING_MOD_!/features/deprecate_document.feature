Feature: Deprecate a document

  Scenario: A user deprecates an existing document
    Given an existing document with id card
    When I deprecate the document with reason "outdated"
    Then the id card status should be "deprecated"
