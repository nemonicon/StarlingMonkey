import { Minimatch } from './minimatch/index.mjs';
import { braceExpand } from './minimatch/index.mjs';
import { withBudget, preflight, precompile, limits } from './resource-budget.mjs';

export function createMinimatch() {
  return {
    minimatch(path, pattern, options) {
      return withBudget(() => {
        preflight(path, pattern);
        // Node's windowsPathsNoEscape policy normalizes before brace parsing.
        const normalized = pattern.replace(/\\/g, '/');
        const patterns = braceExpand(normalized, { braceExpandMax: limits.braceAlternatives });
        precompile(path, patterns);
        for (const expanded of patterns) {
          const matcher = new Minimatch(expanded, { ...options, nobrace: true,
            braceExpandMax: limits.braceAlternatives, maxGlobstarRecursion: limits.globstarRecursion });
          if (matcher.match(path)) return true;
        }
        return false;
      });
    },
  };
}
