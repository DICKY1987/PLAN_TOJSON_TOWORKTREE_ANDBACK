Feature: Rename a document identifier

  Scenario: A user renames a document key
    Given an existing document with id card
    When I rekey the document to "NEW_KEY"
    Then the id card should include the old key in aliases
