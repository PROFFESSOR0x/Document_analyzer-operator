"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { SearchBar } from "@/components/domain/search-bar"
import { Upload, FileText, Network, Search, Plus, Trash2 } from "lucide-react"
import { useState } from "react"
import toast from "react-hot-toast"

const mockDocuments = [
  { id: "1", name: "Architecture.pdf", type: "document", size: "2.4 MB", uploaded: "2 hours ago" },
  { id: "2", name: "API Documentation.md", type: "document", size: "156 KB", uploaded: "1 day ago" },
  { id: "3", name: "User Guide.docx", type: "document", size: "1.1 MB", uploaded: "3 days ago" },
]

const mockEntities = [
  { id: "1", type: "concept", label: "Agent Orchestration", connections: 5 },
  { id: "2", type: "concept", label: "Workflow Engine", connections: 3 },
  { id: "3", type: "fact", label: "FastAPI Backend", connections: 2 },
  { id: "4", type: "relationship", label: "Agent → Task", connections: 8 },
]

export default function KnowledgePage() {
  const [search, setSearch] = useState("")

  const handleUpload = () => {
    toast.success("Upload dialog would open here")
  }

  const handleDelete = (id: string) => {
    toast.success(`Document ${id} deleted`)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
            <p className="text-muted-foreground">Manage documents and knowledge entities</p>
          </div>
          <Button onClick={handleUpload}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Document
          </Button>
        </div>

        <Tabs defaultValue="documents" className="space-y-4">
          <TabsList>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="graph">Knowledge Graph</TabsTrigger>
            <TabsTrigger value="search">Semantic Search</TabsTrigger>
          </TabsList>

          <TabsContent value="documents" className="space-y-4">
            <div className="flex items-center gap-4">
              <SearchBar
                placeholder="Search documents..."
                value={search}
                onChange={setSearch}
                className="flex-1 max-w-sm"
              />
            </div>

            <ScrollArea className="h-[500px]">
              <div className="space-y-2">
                {mockDocuments.map((doc) => (
                  <Card key={doc.id}>
                    <CardContent className="flex items-center justify-between p-4">
                      <div className="flex items-center gap-4">
                        <FileText className="h-8 w-8 text-primary" />
                        <div>
                          <p className="font-medium">{doc.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {doc.size} • Uploaded {doc.uploaded}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">View</Button>
                        <Button variant="destructive" size="sm" onClick={() => handleDelete(doc.id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="graph" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Network className="h-5 w-5" />
                  Knowledge Graph
                </CardTitle>
                <CardDescription>Interactive visualization of knowledge entities and relationships</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex h-96 items-center justify-center rounded-lg border bg-muted/50">
                  <div className="text-center text-muted-foreground">
                    <Network className="mx-auto h-12 w-12 mb-4" />
                    <p>Interactive graph visualization would be rendered here</p>
                    <p className="text-sm">Using React Flow or D3.js</p>
                  </div>
                </div>

                <div className="mt-4 space-y-2">
                  <h3 className="font-medium">Entities</h3>
                  <div className="flex flex-wrap gap-2">
                    {mockEntities.map((entity) => (
                      <Badge key={entity.id} variant="outline">
                        {entity.label} ({entity.type})
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="search" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  Semantic Search
                </CardTitle>
                <CardDescription>Search knowledge base using natural language</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input placeholder="Ask a question or search for concepts..." className="flex-1" />
                  <Button>
                    <Search className="mr-2 h-4 w-4" />
                    Search
                  </Button>
                </div>

                <div className="rounded-lg border p-4">
                  <p className="text-sm text-muted-foreground">
                    Enter a search query to find relevant knowledge entities
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
