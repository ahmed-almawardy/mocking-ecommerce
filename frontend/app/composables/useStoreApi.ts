/** Same-origin API calls in the browser; private Docker-network base URL during SSR. */
export function useStoreApi() {
  const config = useRuntimeConfig()
  const baseURL = import.meta.server
    ? `${String(config.apiInternalBase).replace(/\/$/, '')}/api/v1`
    : '/api/v1'
  return $fetch.create({ baseURL })
}
