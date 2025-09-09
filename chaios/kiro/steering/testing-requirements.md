---
inclusion: fileMatch
fileMatchPattern: "test/**/*.dart"
---

# Testing Standards for ChaiOS

## Test Coverage Requirements
- Maintain minimum 80% code coverage for all business logic
- Ensure 100% coverage for critical payment and inventory operations
- All public methods must have comprehensive unit tests
- Critical user flows must have integration tests
- Mock external dependencies appropriately in unit tests
- Test both success and failure scenarios thoroughly

## Test Structure and Organization
- Use descriptive test names that explain the scenario being tested
- Follow Arrange-Act-Assert pattern consistently
- Group related tests using `group()` function for organization
- Use `setUp()` and `tearDown()` for proper test preparation and cleanup
- Organize tests to mirror the source code structure
- Separate unit, widget, and integration tests clearly

## Test Data Management
- Use factory methods for creating consistent test objects
- Avoid hardcoded test data where possible for maintainability
- Create realistic test scenarios that match actual usage patterns
- Use builders pattern for complex test object creation
- Implement test data cleanup to prevent test interference
- Use meaningful test data that represents real business scenarios

## Testing Best Practices
- Test one thing at a time for clarity and maintainability
- Use meaningful assertions that clearly indicate what is being verified
- Avoid testing implementation details, focus on behavior
- Write tests before implementing features (TDD approach)
- Ensure tests are deterministic and not dependent on external factors
- Regularly review and refactor tests to maintain quality