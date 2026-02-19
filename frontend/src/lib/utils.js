import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatDate(date) {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function getStatusColor(status) {
  const colors = {
    PASSED: 'text-green-600 bg-green-50 border-green-200',
    PARTIAL: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    FAILED: 'text-red-600 bg-red-50 border-red-200',
    RUNNING: 'text-blue-600 bg-blue-50 border-blue-200',
  }
  return colors[status] || colors.FAILED
}

export function getErrorTypeColor(type) {
  const colors = {
    LINTING: 'bg-purple-100 text-purple-800',
    SYNTAX: 'bg-red-100 text-red-800',
    LOGIC: 'bg-orange-100 text-orange-800',
    TYPE_ERROR: 'bg-pink-100 text-pink-800',
    IMPORT: 'bg-blue-100 text-blue-800',
    INDENTATION: 'bg-gray-100 text-gray-800',
    UNKNOWN: 'bg-gray-100 text-gray-800',
  }
  return colors[type] || colors.UNKNOWN
}
