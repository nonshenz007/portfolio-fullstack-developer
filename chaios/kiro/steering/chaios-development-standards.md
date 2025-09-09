---
inclusion: always
---

# ChaiOS Development Standards

## Code Style Guidelines
- Use meaningful variable and function names that clearly describe their purpose
- Follow Dart naming conventions (camelCase for variables, PascalCase for classes)
- Add comprehensive documentation comments for all public APIs
- Maintain consistent indentation (2 spaces) throughout the codebase
- Use const constructors where possible for performance optimization
- Prefer composition over inheritance for widget design
- Keep functions small and focused on a single responsibility

## Architecture Patterns
- Follow the established feature-based architecture strictly
- Use Repository pattern for all data access operations
- Implement Provider pattern for state management consistently
- Separate business logic from UI components completely
- Use dependency injection for testability and maintainability
- Implement proper error boundaries at each architectural layer
- Follow SOLID principles in class design

## Error Handling Standards
- Always handle exceptions at appropriate architectural levels
- Provide user-friendly error messages that guide user actions
- Log errors comprehensively for debugging and monitoring
- Use custom exception types for different error categories
- Implement graceful degradation for non-critical failures
- Never expose technical error details to end users
- Provide retry mechanisms for transient failures

## Performance Requirements
- Maintain 60fps UI performance at all times
- Implement lazy loading for large data sets
- Use efficient data structures and algorithms
- Profile and optimize database queries
- Minimize widget rebuilds through proper state management
- Implement proper memory management and resource disposal

## Security Standards
- Validate all user inputs at entry points
- Encrypt sensitive data in local storage
- Use secure communication protocols exclusively
- Implement proper access control mechanisms
- Log security-related events for audit trails
- Follow principle of least privilege for data access