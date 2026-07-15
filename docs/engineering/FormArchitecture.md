# Form Architecture â€” Second Brain OS

| Field | Value |
|---|---|
| Document ID | ENG-FRM-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-12 |
| Applies To | `apps/web/` â€” All CRUD forms across 17 modules |

---

## Table of Contents

1. [Stack Overview](#1-stack-overview)
2. [Form Pattern Catalog](#2-form-pattern-catalog)
3. [Zod Validation Schemas](#3-zod-validation-schemas)
4. [Form Component Library](#4-form-component-library)
5. [Submission Patterns](#5-submission-patterns)
6. [Error Handling](#6-error-handling)
7. [Async Operations & Loading](#7-async-operations--loading)
8. [Form Persistence & Drafts](#8-form-persistence--drafts)
9. [Module-Specific Form Schemas](#9-module-specific-form-schemas)
10. [Cross-Cutting Concerns](#10-cross-cutting-concerns)
11. [Testing Forms](#11-testing-forms)

---

### Architecture Diagram â€” Form State Machine & Validation Pipeline

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#6366F1',
      'primaryTextColor': '#F1F5F9',
      'primaryBorderColor': '#6366F1',
      'lineColor': '#818CF8',
      'secondaryColor': '#13151A',
      'tertiaryColor': '#0A0B0F',
      'clusterBkg': '#0A0B0F',
      'clusterBorder': '#334155',
      'nodeBorder': '#6366F1',
      'nodeTextColor': '#F1F5F9',
      'edgeLabelBackground': '#13151A',
      'fontFamily': 'DM Sans',
      'titleColor': '#F1F5F9'
    }
  }
}%%
graph TD
    subgraph States["Form States"]
        IDLE["IDLE<br/>Initial / Reset"]
        FOCUS["FOCUSED<br/>Field Active"]
        DIRTY["DIRTY<br/>Value Changed"]
        VALIDATING["VALIDATING<br/>Zod Schema Check"]
        INVALID["INVALID<br/>Validation Errors"]
        VALID["VALID<br/>Ready to Submit"]
        SUBMITTING["SUBMITTING<br/>API Call in Flight"]
        SUCCESS["SUCCESS<br/>Submission Complete"]
        ERROR["ERROR<br/>API / Network Failure"]
    end
    subgraph Transitions["Transition Triggers"]
        UserInput["User Input"]
        Blur["Field Blur"]
        Debounce["Debounce 300ms"]
        Submit["Submit Click"]
        APISuccess["API 2xx"]
        APIFail["API 4xx/5xx"]
    end
    IDLE --> FOCUS: Focus
    FOCUS --> DIRTY: UserInput
    DIRTY --> VALIDATING: Debounce
    VALIDATING --> VALID: No Errors
    VALIDATING --> INVALID: Errors Found
    INVALID --> DIRTY: UserInput
    FOCUS --> IDLE: Blur + Empty
    VALID --> SUBMITTING: Submit
    INVALID --> SUBMITTING: Submit (force)
    SUBMITTING --> SUCCESS: APISuccess
    SUBMITTING --> ERROR: APIFail
    ERROR --> DIRTY: UserInput
    ERROR --> IDLE: Reset
    SUCCESS --> IDLE: Reset
```

---

## 1. Stack Overview

### 1.1 Technology Decisions

| Tool | Version | Purpose | Alternative Considered |
|---|---|---|---|
| `react-hook-form` | ^7.49 | Form state management, validation trigger, submission | Formik, Final Form |
| `zod` | ^3.22 | Schema-based validation with TypeScript inference | Yup, Joi, io-ts |
| `@hookform/resolvers` | ^3.3 | Bridge between Zod + react-hook-form | Manual validation |
| `react-textarea-autosize` | ^8.5 | Auto-growing textareas | Manual CSS |

### 1.2 Why react-hook-form + Zod

| Reason | Detail |
|---|---|
| **Performance** | Uncontrolled inputs by default â€” minimal re-renders (only changed field updates, not entire form) |
| **Type inference** | `z.infer<typeof TaskSchema>` generates TypeScript types directly from validation schema â€” single source of truth |
| **Bundle size** | react-hook-form: ~9KB gzipped, Zod: ~8KB gzipped |
| **Native validation** | Each input registers independently â€” no wrapper component needed |
| **Resolver pattern** | Validation logic separated from UI â€” easy to swap or test independently |

### 1.3 Import Pattern

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
```

---

## 2. Form Pattern Catalog

### 2.1 Form Categories

| Category | Example | Pattern | Modal/Inline |
|---|---|---|---|
| **Quick Create** | Add Task (title only) | Single field, no validation | Inline / Cmd+K |
| **Full Create** | New Course (all fields) | Multi-field, full validation | Modal |
| **Edit** | Edit Task | Pre-populated, partial validation | Modal / Slide panel |
| **Bulk Action** | Batch complete tasks | Checkbox list + confirm | Modal |
| **Settings** | Profile update | Key-value pairs, auto-save | Page / Panel |
| **Search** | Filter tasks | Controlled inputs, debounced | Inline |
| **AI Prompt** | Chat message | Single textarea, no validation | Inline |

### 2.2 Form Mode Decision Matrix

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                       WHAT KIND OF FORM?                                â”‚
â”‚                                                                          â”‚
â”‚  Is this a CREATE or EDIT operation?                                     â”‚
â”‚  â”œâ”€â”€ CREATE â†’ How many fields?                                           â”‚
â”‚  â”‚            â”œâ”€â”€ 1-3 fields  â†’ Quick Create (inline form)              â”‚
â”‚  â”‚            â””â”€â”€ 4+ fields   â†’ Full Create (modal form)                â”‚
â”‚  â””â”€â”€ EDIT    â†’ Is data complex?                                          â”‚
â”‚                â”œâ”€â”€ Yes â†’ Modal with pre-populated fields                 â”‚
â”‚                â””â”€â”€ No  â†’ Inline editable text (click to edit)           â”‚
â”‚                                                                          â”‚
â”‚  Is the form for SETTINGS or CONFIG?                                     â”‚
â”‚  â””â”€â”€ Yes â†’ Auto-save on blur / debounced save                           â”‚
â”‚                                                                          â”‚
â”‚  Is this for SEARCH or FILTER?                                           â”‚
â”‚  â””â”€â”€ Yes â†’ Controlled inputs, debounced (300ms), URL-synced             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 2.3 Form Outline Per Module

| Module | Create Pattern | Edit Pattern | Fields | Validation |
|---|---|---|---|---|
| Tasks | Modal (2 columns) | Modal | 8 fields | Zod |
| Courses | Modal | Modal | 6 fields | Zod |
| Goals | Modal (roadmap) | Slide panel | 7 fields | Zod |
| Habits | Quick inline | Modal | 5 fields | Zod |
| Sleep | Quick inline | N/A | 3 fields | Native |
| Income | Modal | Modal | 6 fields | Zod |
| Projects | Modal | Slide panel | 8 fields | Zod |
| Ideas | Quick inline | Modal | 4 fields | Minimal |
| Resources | Modal | Modal | 5 fields | Zod |
| Opportunities | Auto-generated | Edit modal | 6 fields | Zod |
| Time | Quick inline + modal | Modal | 5 fields | Native |
| Academics | Modal | Modal | 7 fields | Zod |
| YouTube | Modal | Modal | 4 fields | Minimal |
| Automation | Toggle panel | Toggle panel | 3 fields | None |
| Chat | Single textarea | N/A | 1 field | None |

---

## 3. Zod Validation Schemas

### 3.1 Schema Architecture

Every module has one Zod schema file at `apps/web/types/` that serves BOTH validation and TypeScript types:

```typescript
// apps/web/types/task.ts
import { z } from 'zod'

// 1. Define the Zod schema (single source of truth)
export const TaskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(200, 'Title must be under 200 characters'),
  description: z.string()
    .max(2000, 'Description must be under 2000 characters')
    .optional()
    .or(z.literal('')),
  priority: z.enum(['low', 'medium', 'high', 'urgent'], {
    errorMap: () => ({ message: 'Select a priority level' }),
  }),
  category: z.enum(['study', 'project', 'habit', 'personal', 'income']),
  estimated_minutes: z.coerce.number()
    .int('Must be a whole number')
    .min(5, 'Minimum 5 minutes')
    .max(480, 'Maximum 8 hours')
    .optional()
    .nullable(),
  due_date: z.string()
    .optional()
    .nullable(),
  dependency_id: z.string().uuid().optional().nullable(),
  is_recurring: z.boolean().default(false),
  recurring_frequency: z.enum(['daily', 'weekly', 'monthly']).optional().nullable(),
})

// 2. Infer the TypeScript type from the schema
export type TaskFormData = z.infer<typeof TaskSchema>

// 3. Create-specific schema (strict)
export const TaskCreateSchema = TaskSchema.required({ title: true, priority: true })

// 4. Update-specific schema (partial)
export const TaskUpdateSchema = TaskSchema.partial()
```

### 3.2 Schema Rules

| Rule | Rationale | Enforcement |
|---|---|---|
| Every schema has both `Create` and `Update` variants | Create requires all required fields; Update allows partial | Convention |
| `z.coerce.number()` for numeric inputs | HTML inputs return strings; coerce handles conversion | Linter |
| `.optional().nullable()` for optional fields | HTML forms submit empty strings, not undefined | Type check |
| Error messages on every `.min()`/`.max()` | User-facing messages, not Zod defaults | Code review |
| `z.enum()` with explicit `errorMap` | Better UX than Zod's generic enum error | Convention |

### 3.3 Validation Timing

| Trigger | When | What Happens |
|---|---|---|
| `onBlur` | Field loses focus | Single field validation |
| `onChange` (mode: 'onChange') | Every keystroke | Real-time validation (for UX-critical fields) |
| `onSubmit` | Form submit | Full schema validation |
| Manual `trigger()` | Programmatic | Validate specific fields |

**Default mode:** `onSubmit` + `onBlur` (performance + UX balance)

```typescript
const form = useForm<TaskFormData>({
  resolver: zodResolver(TaskSchema),
  mode: 'onBlur',       // Validate on blur
  reValidateMode: 'onChange',  // Re-validate as user corrects
  defaultValues: {
    title: '',
    priority: 'medium',
    category: 'personal',
    estimated_minutes: 30,
  },
})
```

### 3.4 Cross-Field Validation

```typescript
// Conditional validation: if recurring, frequency is required
export const TaskSchema = z.object({
  is_recurring: z.boolean(),
  recurring_frequency: z.enum(['daily', 'weekly', 'monthly']).optional().nullable(),
}).refine(
  (data) => !data.is_recurring || data.recurring_frequency,
  { message: 'Select frequency for recurring task', path: ['recurring_frequency'] }
)
```

---

## 4. Form Component Library

### 4.1 Component Hierarchy

```
FormPage / Modal
â”œâ”€â”€ FormProvider (react-hook-form context)
â”‚   â”œâ”€â”€ FormField (wrapper component)
â”‚   â”‚   â”œâ”€â”€ Label
â”‚   â”‚   â”œâ”€â”€ Input / Select / Textarea / Checkbox
â”‚   â”‚   â””â”€â”€ ErrorMessage
â”‚   â”œâ”€â”€ FormSection (grouping)
â”‚   â””â”€â”€ FormActions (Submit + Cancel)
```

### 4.2 FormField Wrapper

```typescript
// components/FormField.tsx
interface FormFieldProps {
  name: string
  label: string
  required?: boolean
  helperText?: string
  children: (props: { value: any; onChange: (...event: any[]) => void; onBlur: () => void; ref: any; error?: string }) => React.ReactNode
}

export function FormField({ name, label, required, helperText, children }: FormFieldProps) {
  const { control, formState: { errors } } = useFormContext()
  const fieldError = errors[name]?.message as string | undefined

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <div className="space-y-2">
          <Label htmlFor={name} required={required}>{label}</Label>
          {children(field)}
          {fieldError && <ErrorMessage message={fieldError} />}
          {helperText && !fieldError && <HelperText>{helperText}</HelperText>}
        </div>
      )}
    />
  )
}
```

### 4.3 Label Component

```typescript
// components/ui/Label.tsx
interface LabelProps {
  htmlFor: string
  required?: boolean
  children: React.ReactNode
}

export function Label({ htmlFor, required, children }: LabelProps) {
  return (
    <label
      htmlFor={htmlFor}
      className="block text-sm font-medium text-text-primary"
    >
      {children}
      {required && <span className="text-accent-error ml-1" aria-hidden="true">*</span>}
    </label>
  )
}
```

### 4.4 ErrorMessage Component

```typescript
// components/ui/ErrorMessage.tsx
interface ErrorMessageProps {
  message: string
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <p className="text-xs text-accent-error flex items-center gap-1" role="alert" aria-live="assertive">
      <AlertCircle size={12} />
      {message}
    </p>
  )
}
```

### 4.5 Input Component (Registered)

```typescript
// components/ui/Input.tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ error, className = '', ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={clsx(
          'input',
          error && 'border-accent-error focus:ring-accent-error',
          className
        )}
        aria-invalid={error ? 'true' : undefined}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'
```

### 4.6 Select Component (Registered)

```typescript
// components/ui/Select.tsx
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: boolean
  options: { value: string; label: string }[]
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ error, options, className = '', ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={clsx('input capitalize', error && 'border-accent-error', className)}
        aria-invalid={error ? 'true' : undefined}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    )
  }
)
Select.displayName = 'Select'
```

### 4.7 Textarea Component (Registered + Auto-size)

```typescript
// components/ui/Textarea.tsx
import TextareaAutosize from 'react-textarea-autosize'

interface TextareaProps {
  error?: boolean
  minRows?: number
  maxRows?: number
  [key: string]: any
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ error, minRows = 3, maxRows = 8, ...props }, ref) => {
    return (
      <TextareaAutosize
        ref={ref}
        minRows={minRows}
        maxRows={maxRows}
        className={clsx('input resize-none', error && 'border-accent-error')}
        aria-invalid={error ? 'true' : undefined}
        {...props}
      />
    )
  }
)
Textarea.displayName = 'Textarea'
```

### 4.8 DatePicker (Native)

```typescript
// Usage: Native HTML date input wrapped in FormField
<FormField name="due_date" label="Due Date">
  {({ value, onChange, onBlur, ref }) => (
    <Input
      ref={ref}
      type="date"
      value={value || ''}
      onChange={onChange}
      onBlur={onBlur}
    />
  )}
</FormField>
```

### 4.9 Checkbox (Boolean toggle)

```typescript
interface CheckboxProps {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}

export function Checkbox({ label, checked, onChange }: CheckboxProps) {
  return (
    <label className="flex items-center gap-3 cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="w-4 h-4 rounded border-border text-accent-primary focus:ring-accent-primary"
      />
      <span className="text-sm text-text-secondary">{label}</span>
    </label>
  )
}
```

### 4.10 FormActions (Submit + Cancel)

```typescript
interface FormActionsProps {
  onCancel: () => void
  submitLabel?: string
  isLoading?: boolean
  disabled?: boolean
}

export function FormActions({ onCancel, submitLabel = 'Save', isLoading, disabled }: FormActionsProps) {
  return (
    <div className="flex gap-3 pt-4 border-t border-border mt-6">
      <button type="button" onClick={onCancel} className="btn btn-secondary flex-1">
        Cancel
      </button>
      <button
        type="submit"
        disabled={disabled || isLoading}
        className="btn btn-primary flex-1 gap-2"
      >
        {isLoading && <Loader2 size={16} className="animate-spin" />}
        {isLoading ? 'Saving...' : submitLabel}
      </button>
    </div>
  )
}
```

---

## 5. Submission Patterns

### 5.1 Standard Create Flow

```typescript
'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { TaskSchema, TaskFormData } from '@/types/task'
import { useTaskStore } from '@/lib/taskStore'

export function AddTaskModal({ onClose }: { onClose: () => void }) {
  const { addTask } = useTaskStore()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<TaskFormData>({
    resolver: zodResolver(TaskSchema),
    mode: 'onBlur',
    defaultValues: {
      title: '',
      priority: 'medium',
      category: 'personal',
      estimated_minutes: 30,
    },
  })

  const onSubmit = async (data: TaskFormData) => {
    setIsSubmitting(true)
    try {
      await addTask({
        ...data,
        due_date: data.due_date || undefined,
        is_recurring: data.is_recurring,
        recurring_frequency: data.is_recurring ? data.recurring_frequency : undefined,
        status: 'pending',
      })
      toast.success('Task created')
      onClose()
    } catch (err: any) {
      toast.error(err.message || 'Failed to create task')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
      <FormActions onCancel={onClose} isLoading={isSubmitting} submitLabel="Create Task" />
    </form>
  )
}
```

### 5.2 Standard Edit Flow (Pre-populated)

```typescript
export function EditTaskModal({ task, onClose }: { task: Task; onClose: () => void }) {
  const { updateTask } = useTaskStore()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<TaskFormData>({
    resolver: zodResolver(TaskSchema),
    defaultValues: {
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      category: task.category,
      estimated_minutes: task.estimated_minutes || 30,
      due_date: task.due_date ? task.due_date.split('T')[0] : '',
    },
  })

  const onSubmit = async (data: TaskFormData) => {
    setIsSubmitting(true)
    try {
      await updateTask(task.id, data)
      toast.success('Task updated')
      onClose()
    } catch (err: any) {
      toast.error(err.message || 'Failed to update task')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <FormActions onCancel={onClose} isLoading={isSubmitting} submitLabel="Save Changes" />
    </form>
  )
}
```

### 5.3 Optimistic Update Pattern

```typescript
// For instant UI feedback on high-confidence actions
const onSubmit = async (data: TaskFormData) => {
  const previousTasks = useTaskStore.getState().tasks

  // 1. Optimistic update
  useTaskStore.setState({
    tasks: previousTasks.map(t =>
      t.id === task.id ? { ...t, ...data } : t
    ),
  })

  try {
    // 2. Actual API call
    await updateTask(task.id, data)
  } catch (err) {
    // 3. Rollback on failure
    useTaskStore.setState({ tasks: previousTasks })
    toast.error('Failed to save. Reverted changes.')
  }
}
```

### 5.4 Debounced Auto-Save (Settings)

```typescript
export function SettingsForm() {
  const { updateProfile } = useUserStore()
  const form = useForm({ defaultValues: { name: user.name, bio: user.bio } })
  const { watch } = form

  // Auto-save on any field change with 1.5s debounce
  useEffect(() => {
    const subscription = watch((data) => {
      const timer = setTimeout(async () => {
        await updateProfile(data)
        toast.success('Saved')
      }, 1500)
      return () => clearTimeout(timer)
    })
    return () => subscription.unsubscribe()
  }, [watch, updateProfile])
}
```

---

## 6. Error Handling

### 6.1 Validation Error Display

```
+--------------------------------------------------------------------+
|  Label (text-text-primary, text-sm, font-medium)                    |
|                                                                     |
|  +--------------------------------------------------------------+  |
|  | Input value                                      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” |  |
|  |                                                   â”‚ âš  icon   â”‚ |  |
|  |                                                   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ |  |
|  +--------------------------------------------------------------+  |
|    border: accent-error (1px solid #EF4444)                        |
|    ring: focus-ring-error (0 0 0 2px #EF4444)                     |
|                                                                     |
|  âš  Title is required (text-xs, text-accent-error, flex, gap-1)    |
|    role="alert", aria-live="assertive"                              |
+--------------------------------------------------------------------+
```

### 6.2 Server Error Handling

```typescript
const onSubmit = async (data: TaskFormData) => {
  setIsSubmitting(true)
  setServerError(null)
  try {
    const { error } = await supabase.from('tasks').insert(data)
    if (error) {
      // Map Supabase error to field-level error
      if (error.code === '23505') { // unique violation
        form.setError('title', { message: 'A task with this title already exists' })
      } else if (error.code === '23503') { // foreign key violation
        form.setError('dependency_id', { message: 'Referenced task not found' })
      } else {
        setServerError(error.message)
      }
      return
    }
    onClose()
  } catch (err: any) {
    setServerError(err.message || 'Unexpected error occurred')
  } finally {
    setIsSubmitting(false)
  }
}
```

### 6.3 Error State Matrix

| Error Source | Detection | User Message | Recovery |
|---|---|---|---|
| Client validation | `formState.errors` | Per-field message | Fix input |
| Supabase constraint | Error code mapping | "A task with this title already exists" | Change value |
| Supabase auth | 401 response | "Session expired. Please sign in again." | Redirect to login |
| Network | `fetch` throws | "Connection lost. Please check your internet." | Retry button |
| Rate limiting | 429 response | "Too many requests. Try again in 60 seconds." | Countdown + auto-retry |
| Server (5xx) | 500 response | "Something went wrong. Please try again." | Retry button |

### 6.4 Global Error Boundary for Forms

```typescript
// app/global-error.tsx â€” catches uncaught form errors
'use client'
export default function GlobalError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <html>
      <body className="font-body bg-background-page text-text-primary">
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="card max-w-lg text-center space-y-4">
            <h1 className="text-2xl font-display font-bold text-gradient">Something went wrong</h1>
            <p className="text-text-secondary">An unexpected error occurred. Please try again.</p>
            <button onClick={reset} className="btn btn-primary">Try Again</button>
          </div>
        </div>
      </body>
    </html>
  )
}
```

---

## 7. Async Operations & Loading

### 7.1 Submit Loading State

Every submit button follows this pattern:

| State | UI | Disabled? |
|---|---|---|
| Idle | "Save" / "Create Task" | No |
| Submitting | `<Loader2 className="animate-spin" />` + "Saving..." | Yes |
| Success | Dismiss modal / show toast | â€” |
| Error | Show error, re-enable button | No |

### 7.2 Submit Flow Diagram

```
User clicks "Save"
        â”‚
        â–¼
  â”Œâ”€ form.handleSubmit(onSubmit)
  â”‚   Validates all fields
  â”‚   â”‚
  â”‚   â”œâ”€â”€ Invalid â†’ Focus first error field, show errors
  â”‚   â”‚
  â”‚   â””â”€â”€ Valid
  â”‚         â”‚
  â”‚         â–¼
  â”‚   setIsSubmitting(true)
  â”‚   â”‚
  â”‚   â–¼
  â”‚   Call store action (e.g., addTask)
  â”‚   â”‚
  â”‚   â”œâ”€â”€ Success â†’ toast.success, onClose()
  â”‚   â””â”€â”€ Error   â†’ toast.error, setServerError, setIsSubmitting(false)
  â”‚
  â””â”€ form.reset() (optional)
```

### 7.3 Preventing Double Submit

```typescript
<button
  type="submit"
  disabled={isSubmitting || !form.formState.isValid}
  className="btn btn-primary"
>
  {isSubmitting ? 'Saving...' : 'Submit'}
</button>
```

---

## 8. Form Persistence & Drafts

### 8.1 Draft Storage

For forms where user might navigate away:

```typescript
export function useFormDraft<T>(key: string, schema: z.ZodSchema<T>) {
  const STORAGE_KEY = `draft_${key}`

  // Load draft from localStorage on mount
  const loadDraft = (): Partial<T> | null => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (!saved) return null
      return JSON.parse(saved)
    } catch {
      return null
    }
  }

  // Save draft on form changes
  const saveDraft = (data: Partial<T>) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  }

  // Clear draft after successful submit
  const clearDraft = () => {
    localStorage.removeItem(STORAGE_KEY)
  }

  return { loadDraft, saveDraft, clearDraft, STORAGE_KEY }
}

// Usage in form component
const { loadDraft, saveDraft, clearDraft } = useFormDraft('task', TaskSchema)
const form = useForm({
  resolver: zodResolver(TaskSchema),
  defaultValues: loadDraft() || { /* defaults */ },
})

// Auto-save draft on changes
useEffect(() => {
  const sub = form.watch((data) => saveDraft(data))
  return () => sub.unsubscribe()
}, [])

// Clear on successful submit
const onSubmit = async (data: TaskFormData) => {
  await addTask(data)
  clearDraft()
  onClose()
}
```

### 8.2 Navigation Guard

```typescript
// Prevent accidental navigation with unsaved changes
export function useUnsavedChanges(isDirty: boolean) {
  const router = useRouter()

  useEffect(() => {
    const handler = () => {
      if (isDirty) {
        return 'You have unsaved changes. Are you sure you want to leave?'
      }
    }
    router.events.on('routeChangeStart', handler)
    return () => router.events.off('routeChangeStart', handler)
  }, [isDirty, router])

  // Also handle browser refresh/close
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault()
      }
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [isDirty])
}
```

---

## 9. Module-Specific Form Schemas

### 9.1 Tasks

```typescript
export const TaskFormSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(2000).optional().or(z.literal('')),
  priority: z.enum(['low', 'medium', 'high', 'urgent']),
  category: z.enum(['study', 'project', 'habit', 'personal', 'income']),
  estimated_minutes: z.coerce.number().int().min(5).max(480).optional().nullable(),
  due_date: z.string().optional().nullable(),
  dependency_id: z.string().uuid().optional().nullable(),
  is_recurring: z.boolean().default(false),
  recurring_frequency: z.enum(['daily', 'weekly', 'monthly']).optional().nullable(),
})
```

### 9.2 Courses

```typescript
export const CourseFormSchema = z.object({
  name: z.string().min(1, 'Course name is required').max(200),
  platform: z.string().optional(),
  instructor: z.string().optional(),
  total_modules: z.coerce.number().int().min(1).optional().nullable(),
  completed_modules: z.coerce.number().int().min(0).default(0),
  deadline: z.string().optional().nullable(),
  url: z.string().url('Invalid URL').optional().or(z.literal('')),
  notes: z.string().max(5000).optional().or(z.literal('')),
})
```

### 9.3 Goals

```typescript
export const GoalFormSchema = z.object({
  title: z.string().min(1, 'Goal title is required').max(200),
  description: z.string().max(2000).optional().or(z.literal('')),
  category: z.enum(['academic', 'career', 'skill', 'fitness', 'finance', 'personal']),
  target_date: z.string().optional().nullable(),
  status: z.enum(['active', 'paused', 'completed', 'cancelled']).default('active'),
  progress: z.coerce.number().int().min(0).max(100).default(0),
  milestones: z.array(z.object({
    title: z.string().min(1),
    completed: z.boolean().default(false),
  })).optional(),
})
```

### 9.4 Habits

```typescript
export const HabitFormSchema = z.object({
  name: z.string().min(1, 'Habit name is required').max(100),
  description: z.string().max(500).optional().or(z.literal('')),
  frequency: z.enum(['daily', 'weekly', 'weekdays', 'weekends']),
  target_count: z.coerce.number().int().min(1).max(10).default(1),
  category: z.enum(['health', 'learning', 'productivity', 'social', 'creative']),
  color: z.string().regex(/^#[0-9a-fA-F]{6}$/).default('#6366F1'),
})
```

### 9.5 Income

```typescript
export const IncomeFormSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  amount: z.coerce.number().positive('Amount must be positive'),
  category: z.enum(['freelance', 'salary', 'gift', 'investment', 'other']),
  source: z.string().optional(),
  date: z.string().optional().nullable(),
  notes: z.string().max(1000).optional().or(z.literal('')),
  hourly_rate: z.coerce.number().positive().optional().nullable(),
  hours_worked: z.coerce.number().positive().optional().nullable(),
})
```

### 9.6 Projects

```typescript
export const ProjectFormSchema = z.object({
  name: z.string().min(1, 'Project name is required').max(200),
  description: z.string().max(3000).optional().or(z.literal('')),
  status: z.enum(['planning', 'active', 'paused', 'completed']).default('planning'),
  phase: z.string().optional(),
  github_url: z.string().url('Invalid GitHub URL').optional().or(z.literal('')),
  live_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  tech_stack: z.array(z.string()).optional(),
  blockers: z.string().max(1000).optional().or(z.literal('')),
  start_date: z.string().optional().nullable(),
  target_completion: z.string().optional().nullable(),
})
```

### 9.7 Ideas

```typescript
export const IdeaFormSchema = z.object({
  title: z.string().min(1, 'Idea title is required').max(200),
  description: z.string().max(2000).optional().or(z.literal('')),
  stage: z.enum(['raw', 'validating', 'building', 'shipped', 'archived']).default('raw'),
  tags: z.array(z.string()).optional(),
  references: z.array(z.string().url()).optional(),
})
```

### 9.8 Resources

```typescript
export const ResourceFormSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  url: z.string().url('Enter a valid URL'),
  type: z.enum(['article', 'video', 'book', 'paper', 'tool', 'course', 'other']),
  tags: z.array(z.string()).default([]),
  notes: z.string().max(2000).optional().or(z.literal('')),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']).optional(),
})
```

### 9.9 Opportunities

```typescript
export const OpportunityFormSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  company: z.string().optional(),
  role: z.string().optional(),
  url: z.string().url().optional().or(z.literal('')),
  status: z.enum(['saved', 'applied', 'interviewing', 'offer', 'rejected', 'accepted']).default('saved'),
  deadline: z.string().optional().nullable(),
  notes: z.string().max(2000).optional().or(z.literal('')),
  match_score: z.coerce.number().int().min(0).max(100).optional(),
})
```

### 9.10 Academics (Semester)

```typescript
export const SemesterFormSchema = z.object({
  semester: z.coerce.number().int().min(1).max(8, 'BTech has 8 semesters'),
  year: z.coerce.number().int().min(2024).max(2030),
  start_date: z.string().min(1, 'Start date required'),
  end_date: z.string().min(1, 'End date required'),
  subjects: z.array(z.object({
    name: z.string().min(1),
    code: z.string().optional(),
    credits: z.coerce.number().int().min(1).max(5),
  })).min(1, 'Add at least one subject'),
}).refine(
  (data) => new Date(data.end_date) > new Date(data.start_date),
  { message: 'End date must be after start date', path: ['end_date'] }
)
```

---

## 10. Cross-Cutting Concerns

### 10.1 Keyboard Shortcuts

| Shortcut | Action | When Active |
|---|---|---|
| `Enter` | Submit form | Modal open |
| `Escape` | Close/cancel | Modal open |
| `Tab` / `Shift+Tab` | Navigate fields | Within form |
| `Cmd+Enter` | Quick submit | Textarea focused |

### 10.2 Focus Management

```typescript
// Auto-focus first field on modal open
useEffect(() => {
  if (open) {
    const timer = setTimeout(() => {
      form.setFocus('title')
    }, 100)
    return () => clearTimeout(timer)
  }
}, [open])

// Return focus to trigger element on close
const triggerRef = useRef<HTMLButtonElement>(null)
// ... store ref on trigger button
// On close:
triggerRef.current?.focus()
```

### 10.3 Accessibility Attributes

| Element | Attribute | Value |
|---|---|---|
| Form | `novalidate` | (let react-hook-form handle it) |
| Input error | `aria-invalid` | `"true"` |
| Error message | `role` | `"alert"` |
| Error message | `aria-live` | `"assertive"` |
| Required indicator | `aria-required` | `"true"` |
| Modal form | `aria-modal` | `"true"` |
| Button loading | `aria-busy` | `"true"` |

### 10.4 Responsive Form Layout

| Breakpoint | Layout | Field width |
|---|---|---|
| Desktop (>=1024px) | 2-column grid | 50% each |
| Tablet (768-1023px) | 2-column grid | 50% each |
| Mobile (<768px) | Single column | Full width |

```typescript
// 2-column field grid
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
  <FormField name="priority" label="Priority">
    {/* ... */}
  </FormField>
  <FormField name="category" label="Category">
    {/* ... */}
  </FormField>
</div>
```

### 10.5 Number Input Handling

```typescript
// Coerce string â†’ number in schema
estimated_minutes: z.coerce.number()
  .int('Must be a whole number')
  .min(5, 'Minimum 5 minutes')
  .max(480, 'Maximum 8 hours')

// Input type="number" with min/max
<Input
  type="number"
  min={5}
  max={480}
  step={5}
  {...field}
/>
```

---

## 11. Testing Forms

### 11.1 Unit Test Patterns

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AddTaskModal } from './AddTaskModal'

describe('AddTaskModal', () => {
  it('validates required fields on submit', async () => {
    render(<AddTaskModal onClose={jest.fn()} />)

    // Submit with empty title
    fireEvent.click(screen.getByText('Create Task'))

    await waitFor(() => {
      expect(screen.getByText('Title is required')).toBeInTheDocument()
    })
  })

  it('submits valid form data', async () => {
    const mockAddTask = jest.fn()
    jest.spyOn(useTaskStore.getState(), 'addTask').mockImplementation(mockAddTask)

    render(<AddTaskModal onClose={jest.fn()} />)

    await userEvent.type(screen.getByLabelText(/title/i), 'Test task')
    fireEvent.click(screen.getByText('Create Task'))

    await waitFor(() => {
      expect(mockAddTask).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Test task' })
      )
    })
  })

  it('shows error on API failure', async () => {
    jest.spyOn(useTaskStore.getState(), 'addTask').mockRejectedValue(new Error('API error'))

    render(<AddTaskModal onClose={jest.fn()} />)

    await userEvent.type(screen.getByLabelText(/title/i), 'Test task')
    fireEvent.click(screen.getByText('Create Task'))

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('API error')
    })
  })

  it('clears form after successful submit', async () => {
    const onClose = jest.fn()
    render(<AddTaskModal onClose={onClose} />)

    await userEvent.type(screen.getByLabelText(/title/i), 'Test task')
    fireEvent.click(screen.getByText('Create Task'))

    await waitFor(() => {
      expect(onClose).toHaveBeenCalled()
    })
  })
})
```

### 11.2 Schema Unit Tests

```typescript
import { TaskFormSchema } from '@/types/task'

describe('TaskFormSchema', () => {
  it('accepts valid task data', () => {
    const result = TaskFormSchema.safeParse({
      title: 'Complete assignment',
      priority: 'high',
      category: 'study',
    })
    expect(result.success).toBe(true)
  })

  it('rejects empty title', () => {
    const result = TaskFormSchema.safeParse({ title: '', priority: 'medium', category: 'personal' })
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].path).toContain('title')
    }
  })

  it('rejects invalid priority', () => {
    const result = TaskFormSchema.safeParse({
      title: 'Test',
      priority: 'critical',
      category: 'personal',
    })
    expect(result.success).toBe(false)
  })

  it('coerces string numbers to integers', () => {
    const result = TaskFormSchema.safeParse({
      title: 'Test',
      priority: 'medium',
      category: 'study',
      estimated_minutes: '30',
    })
    expect(result.success).toBe(true)
    if (result.success) {
      expect(typeof result.data.estimated_minutes).toBe('number')
    }
  })
})
```

### 11.3 Integration Test Pattern

```typescript
describe('Tasks Page â€” Create Task Flow', () => {
  it('completes full task creation flow', async () => {
    render(<TasksPage />)

    // Wait for page to load
    await screen.findByText('Tasks')

    // Open add modal
    fireEvent.click(screen.getByText('Add Task'))
    await screen.findByRole('dialog')

    // Fill form
    await userEvent.type(screen.getByLabelText(/title/i), 'Integration test task')
    await userEvent.selectOptions(screen.getByLabelText(/priority/i), 'high')

    // Submit
    fireEvent.click(screen.getByText('Create Task'))

    // Verify task appears in list
    await waitFor(() => {
      expect(screen.getByText('Integration test task')).toBeInTheDocument()
    })
  })
})
```

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-12 | Developer | Initial form architecture documentation |
