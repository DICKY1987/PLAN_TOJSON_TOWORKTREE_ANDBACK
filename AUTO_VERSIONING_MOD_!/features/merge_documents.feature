Feature: Merge multiple documents

  Scenario: Merge two source documents into a target
    Given three existing documents with id cards
    When I consolidate the two source documents into the target
    Then the source documents should be marked as merged into the target
