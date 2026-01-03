# Development Setup

## Initial Setup

1. Navigate to package directory:
   ```bash
   cd packages/npm-package
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Development

- Main class: `index.js`
- Import: `import PromptShield from 'pshield'`
- Run tests: `npm test`

## Publishing to npm

1. Update version in `package.json` (follow [Semantic Versioning](https://semver.org/))
   - Use `npm version patch`, `npm version minor`, or `npm version major`
   - Or manually edit the version field

2. Ensure you're logged in to npm:
   ```bash
   npm login
   ```

3. Publish:
   ```bash
   npm publish
   ```
   (Ask Adilet for npm credentials if needed)

4. Verify:
   ```bash
   npm install pshield --upgrade
   ```

## Troubleshooting

- **Module not found**: Run `npm install`
- **Test errors**: Ensure all dependencies are installed: `npm install`
- **Publish errors**: Check npm login status: `npm whoami`

