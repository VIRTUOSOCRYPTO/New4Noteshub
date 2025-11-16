# 🛡️ Admin Panel Guide

## Overview
The Admin Panel allows authorized users to manage all registered users in NotesHub.

## Access Control
**Admin access is restricted to specific authorized email addresses.**

Current admin email(s): `tortoor8@gmail.com`

To add more admin users, update the `ADMIN_EMAILS` environment variable in `/app/backend/.env`:
```bash
ADMIN_EMAILS=tortoor8@gmail.com,another@email.com
```

Only users with emails in this list will have access to:
- Admin Panel
- Moderation features
- System management tools
- User management

## Features

### 1. Dashboard Statistics
- **Total Users**: View total registered users
- **Departments**: Number of unique departments
- **New Users (7 Days)**: Recent signups in the last week
- **Colleges**: Number of unique colleges

### 2. User Management

#### Search & Filter
- **Search**: Search users by USN or email
- **Department Filter**: Filter by specific department
- **Year Filter**: Filter by academic year (1-4)
- **Clear Filters**: Reset all filters

#### User Table
View all users with the following information:
- USN (University Seat Number)
- Email address
- Department
- Academic Year
- College
- Join date

#### Actions
- **Delete User**: Remove a user and all their associated data
  - Deletes user account
  - Deletes all their notes
  - Deletes their points/gamification data
  - Deletes their bookmarks
  - Deletes their referral data

#### Export Data
- Export user list to CSV file
- Includes: USN, Email, Department, College, Year, Created Date

### 3. Pagination
- View 20 users per page
- Navigate between pages
- Shows total user count

## How to Access

1. **Login** with an authorized admin email address (`tortoor8@gmail.com`)
2. Click **"Admin Panel"** in the navigation menu (only visible to admins)
3. The panel will load automatically

**Note:** If you don't see the "Admin Panel" option in the menu, your account is not configured as an admin.

## API Endpoints

The admin panel uses these backend endpoints:

```
GET  /api/admin/users              - List users with filters
GET  /api/admin/users/stats        - Get user statistics
GET  /api/admin/users/{user_id}    - Get user details
PATCH /api/admin/users/{user_id}   - Update user
DELETE /api/admin/users/{user_id}  - Delete user
```

## Security

- **Authentication Required**: Must be logged in
- **Email-based Authorization**: Only authorized email addresses have access
- **Admin Middleware**: Backend validates admin access on every request using environment variables
- **Confirmation Dialogs**: Delete actions require confirmation
- **Protected Endpoints**: All admin API endpoints require valid admin authentication

## Database Collections Managed

When deleting a user, the following collections are cleaned:
- `users` - User account
- `notes` - User's uploaded notes
- `user_points` - Gamification points
- `bookmarks` - Saved bookmarks
- `referrals` - Referral data

## Tips

1. **Regular Backups**: Always backup before bulk deletions
2. **Use Filters**: Narrow down results before taking action
3. **Export First**: Export data before making changes
4. **Double Check**: Deletions are permanent - always confirm

## Future Enhancements

Potential features to add:
- Edit user details inline
- Bulk actions (delete multiple users)
- User activity logs
- Email users directly from panel
- Advanced analytics
- Role-based permissions
- User suspension (instead of deletion)
