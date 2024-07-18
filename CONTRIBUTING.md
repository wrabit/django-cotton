# Contributing to Django Cotton

First off, thanks for considering to contribute to Cotton! 🎉

The following is a set of guidelines for contributing to Django Cotton (https://github.com/wrabit/django-cotton).

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please open an issue on GitHub with a clear description of the problem, steps to reproduce, and any relevant logs or screenshots.

### Suggesting Enhancements

We welcome suggestions for new features or improvements. Please open an issue on GitHub and describe your idea in detail.

### Pull Requests

1. Fork the repository.
2. Create a new branch (`git checkout -b your_feature`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin your_feature`).
6. Open a pull request.

### Coding Standards

- Follow the existing code style and conventions.
- Write clear and descriptive commit messages.
- Include comments and documentation where necessary.

### Building the Project

The development environment is set up using Docker. To build the project, run the following commands from the project root:

```bash
./dev/docker/bin/build.sh # add 'mac' if you're on ARM chip
./dev/docker/bin/run-dev.sh
```

### Testing

Please ensure that your changes pass all existing tests and, if applicable, add new tests to cover your changes.

```bash
./dev/docker/bin/test.sh # append the test module path to test one module or test method
```

### Documentation

If you are ok to do it and you feel the feature you introduce or change requires documentation changes, please also make changes to the README.md and the docs project. Locally, developing the docs site requires you to:

```bash
./docs/docker/bin/build.sh # add 'mac' if you're on ARM chip
./docs/docker/bin/run-dev.sh
```

Thank you for contributing!
