export interface Resource {
  id: string
  title: string
  type: string
  tags: string[]
  url?: string
  createdAt: string
  description?: string
}

export interface Collection {
  id: string
  name: string
  itemCount: number
  coverColor?: string
  lastEdited?: string
}
