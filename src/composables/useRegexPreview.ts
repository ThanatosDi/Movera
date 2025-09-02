import type { MaybeRef } from 'vue'
import { computed, unref } from 'vue'

/**
 * A composable to preview filename changes based on regex patterns.
 * It provides a renamed preview and an HTML string with highlighted matches.
 *
 * @param filename The original filename.
 * @param src_filename The source regex pattern to match against the filename.
 * @param dst_filename The destination pattern for renaming, using Python-style backreferences (e.g., \1, \2).
 */
export function useRegexPreview(
  filename: MaybeRef<string>,
  src_filename: MaybeRef<string>,
  dst_filename: MaybeRef<string>
) {
  // Convert Python-style backreferences (\1, \2) to JS-style ($1, $2)
  const jsDstFilename = computed(() => {
    try {
      // The replacement string needs to escape '$' so '$$' becomes a literal '$'.
      // We replace '\1' with '$1', '\2' with '$2', etc.
      return unref(dst_filename).replace(/\\(\d)/g, '$$$1')
    } catch {
      return ''
    }
  })

  const result = computed(() => {
    const srcPattern = unref(src_filename)
    const originalFilename = unref(filename)

    if (!srcPattern || !originalFilename) {
      return {
        preview: originalFilename,
        highlighted: originalFilename,
        error: null
      }
    }

    try {
      const regex = new RegExp(srcPattern)
      const match = originalFilename.match(regex)

      if (match) {
        const preview = originalFilename.replace(regex, jsDstFilename.value)
        // Using '$&' in the replacement string inserts the entire matched substring.
        const highlighted = originalFilename.replace(regex, '<span class="bg-yellow-300 rounded p-0.5">$&</span>')

        return {
          preview,
          highlighted,
          error: null
        }
      } else {
        return {
          preview: originalFilename,
          highlighted: originalFilename,
          error: 'No match found.'
        }
      }
    } catch (e: any) {
      return {
        preview: originalFilename,
        highlighted: originalFilename,
        error: e.message
      }
    }
  })

  return {
    preview: computed(() => result.value.preview),
    highlighted: computed(() => result.value.highlighted),
    error: computed(() => result.value.error)
  }
}
