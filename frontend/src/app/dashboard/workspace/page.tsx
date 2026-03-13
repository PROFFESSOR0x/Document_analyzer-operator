"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { FolderOpen, Plus, Trash2, FileCode, Download, Upload, Terminal } from "lucide-react"
import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import toast from "react-hot-toast"

const mockWorkspaces = [
  { id: "1", name: "Project Alpha", description: "Main project workspace", files: 24, created: "2 days ago" },
  { id: "2", name: "Testing", description: "Test environment", files: 8, created: "1 week ago" },
]

const mockFiles = [
  { id: "1", name: "main.py", type: "file", size: "2.4 KB" },
  { id: "2", name: "config.yaml", type: "file", size: "1.1 KB" },
  { id: "3", name: "src", type: "directory", children: 5 },
  { id: "4", name: "README.md", type: "file", size: "3.2 KB" },
]

export default function WorkspacePage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [selectedWorkspace, setSelectedWorkspace] = useState<string | null>(null)

  const handleCreateWorkspace = () => {
    toast.success("Workspace created (mock)")
    setIsCreateOpen(false)
  }

  const handleDeleteWorkspace = (id: string) => {
    toast.success(`Workspace ${id} deleted`)
  }

  const handleUploadFile = () => {
    toast.success("File upload dialog would open here")
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Workspace</h1>
            <p className="text-muted-foreground">Manage project files and resources</p>
          </div>
          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Workspace
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Workspace</DialogTitle>
                <DialogDescription>
                  Create a new workspace for your project
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input id="name" placeholder="My Workspace" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Input id="description" placeholder="Workspace description" />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateWorkspace}>Create</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {mockWorkspaces.map((workspace) => (
            <Card
              key={workspace.id}
              className={`cursor-pointer transition-shadow hover:shadow-md ${
                selectedWorkspace === workspace.id ? "ring-2 ring-primary" : ""
              }`}
              onClick={() => setSelectedWorkspace(workspace.id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <FolderOpen className="h-5 w-5 text-primary" />
                    <CardTitle>{workspace.name}</CardTitle>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteWorkspace(workspace.id)
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <CardDescription>{workspace.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">
                  {workspace.files} files • Created {workspace.created}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {selectedWorkspace && (
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle>Files</CardTitle>
                <CardDescription>Workspace file tree</CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96">
                  <div className="space-y-2">
                    {mockFiles.map((file) => (
                      <div
                        key={file.id}
                        className="flex items-center justify-between rounded-md p-2 hover:bg-accent"
                      >
                        <div className="flex items-center gap-2">
                          {file.type === "directory" ? (
                            <FolderOpen className="h-4 w-4 text-primary" />
                          ) : (
                            <FileCode className="h-4 w-4" />
                          )}
                          <span className="text-sm">{file.name}</span>
                        </div>
                        {file.type === "file" && (
                          <span className="text-xs text-muted-foreground">{file.size}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
                <div className="mt-4 flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1" onClick={handleUploadFile}>
                    <Upload className="mr-2 h-3 w-3" />
                    Upload
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Download className="mr-2 h-3 w-3" />
                    Download
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Editor</CardTitle>
                    <CardDescription>File editor and terminal</CardDescription>
                  </div>
                  <Button variant="outline" size="sm">
                    <Terminal className="mr-2 h-3 w-3" />
                    Open Terminal
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex h-96 items-center justify-center rounded-lg border bg-muted/50">
                  <div className="text-center text-muted-foreground">
                    <FileCode className="mx-auto h-12 w-12 mb-4" />
                    <p>Select a file to edit</p>
                    <p className="text-sm">Monaco Editor would be rendered here</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
