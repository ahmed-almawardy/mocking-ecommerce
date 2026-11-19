export function useAdminApi() {
  const api = useStoreApi()

  function get<T>(path: string, query?: Record<string, string | number | undefined>) {
    return api<T>(`/admin/${path.replace(/^\//, '')}`, { query, credentials: 'include' })
  }

  function post<T>(path: string, body: unknown) {
    return api<T>(`/admin/${path.replace(/^\//, '')}`, { method: 'POST', body, credentials: 'include' })
  }

  function patch<T>(path: string, body: unknown) {
    return api<T>(`/admin/${path.replace(/^\//, '')}`, { method: 'PATCH', body, credentials: 'include' })
  }

  function remove(path: string) {
    return api<void>(`/admin/${path.replace(/^\//, '')}`, { method: 'DELETE', credentials: 'include' })
  }

  function upload(file: File) {
    const body = new FormData()
    body.append('file', file)
    return api<{ url: string; filename: string; content_type: string; size: number }>('/admin/media', {
      method: 'POST', body, credentials: 'include',
    })
  }

  return { get, post, patch, remove, upload }
}
