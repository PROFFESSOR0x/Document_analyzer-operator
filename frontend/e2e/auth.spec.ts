import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login')
    await expect(page).toHaveTitle(/Document Analyzer/)
    await expect(page.getByText('Sign In')).toBeVisible()
  })

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/login')
    await page.getByText('Register').click()
    await expect(page).toHaveURL('/register')
    await expect(page.getByText('Create an account')).toBeVisible()
  })
})

test.describe('Dashboard', () => {
  test('should require authentication', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL('/login')
  })
})
