import js from "@eslint/js";
import prettier from "eslint-config-prettier";
import jsxA11y from "eslint-plugin-jsx-a11y";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
    { ignores: ["dist/", "playwright-report/", "test-results/", "src/mycroft/tokens.ts"] },
    js.configs.recommended,
    tseslint.configs.strictTypeChecked,
    {
        languageOptions: {
            globals: { ...globals.browser, ...globals.node },
            parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
        },
    },
    { files: ["eslint.config.js"], extends: [tseslint.configs.disableTypeChecked] },
    reactHooks.configs.flat["recommended-latest"],
    jsxA11y.flatConfigs.strict,
    {
        // The design system is self-contained: React, its own files, and the contract enums as types.
        files: ["src/mycroft/**/*.{ts,tsx}"],
        ignores: ["src/mycroft/**/*.test.{ts,tsx}"],
        rules: {
            "no-restricted-imports": [
                "error",
                {
                    patterns: [
                        {
                            regex: "^(?!react$|react/|react-dom$|react-dom/|\\./|\\.\\./contract/enums$)",
                            message: "src/mycroft/ imports only React and its own files.",
                        },
                        {
                            regex: "^\\.\\./contract/enums$",
                            allowTypeImports: true,
                            message: "Contract enums are imported as types only.",
                        },
                    ],
                },
            ],
            // Values come from tokens; an inline style may only set a component custom property.
            "no-restricted-syntax": [
                "error",
                {
                    selector:
                        "JSXAttribute[name.name='style'] ObjectExpression > Property > Identifier.key",
                    message: "Inline styles may only set CSS custom properties ('--my-*').",
                },
            ],
        },
    },
    prettier,
);
