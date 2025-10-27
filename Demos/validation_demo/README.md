# zDialog Auto-Validation Demo (Week 5.2)

This demo showcases **automatic form validation** against zSchema rules before submission.

## 🎯 What This Demo Shows

When a `zDialog` includes `model: '@.zSchema.demo_users'`, the form data is **automatically validated** against the schema's validation rules **before** the `onSubmit` action executes.

### Features Demonstrated:

✅ **Username Validation** - Pattern: `^[a-zA-Z0-9_]{3,20}$` (3-20 chars, alphanumeric + underscore)  
✅ **Email Validation** - Format: valid email address  
✅ **Age Validation** - Range: 18-120  
✅ **Phone Validation** - Format: 10-15 digits  
✅ **Website Validation** - Format: valid URL  
✅ **Bio Validation** - Length: max 200 characters  

## 🚀 How to Run

```bash
python3 demo_validation.py
```

## 📋 Try These Scenarios:

### Scenario 1: Valid Data (Should Succeed)
1. Choose: "Add User (With Validation)"
2. Enter:
   - Username: `validuser`
   - Email: `test@example.com`
   - Age: `25`
   - Phone: `+1234567890`
   - Website: `https://example.com`
   - Bio: `This is a valid bio.`
3. ✅ **Result**: User registered successfully!

### Scenario 2: Invalid Data (Should Fail with Errors)
1. Choose: "Add User (Invalid Data - See Errors)"
2. Enter:
   - Username: `ab` ❌ (too short)
   - Email: `not-an-email` ❌ (invalid format)
   - Age: `15` ❌ (below minimum)
   - Phone: `abc` ❌ (invalid format)
   - Website: `not-a-url` ❌ (invalid format)
   - Bio: `(text exceeding 200 chars)` ❌ (too long)
3. 🚫 **Result**: Validation errors displayed, no data inserted!

## 🔑 Key Insight: The Critical Gap Closed

**Before Week 5.2:**
- User fills form → submits → **server validates** → error returned
- Problem: **Wasted round-trip**, poor UX

**After Week 5.2:**
- User fills form → **auto-validates** → errors shown **before submit**
- Benefit: **No wasted round-trip**, immediate feedback!

## 📁 Files

- `zSchema.demo_users.yaml` - Schema with validation rules
- `zUI.validation_demo.yaml` - Interactive menu with forms
- `demo_validation.py` - Demo runner
- `README.md` - This file

## 🎓 How It Works

```yaml
# In zUI.validation_demo.yaml
"^Add User (With Validation)":
  zDialog:
    title: "User Registration"
    model: '@.zSchema.demo_users'  # 🎯 Auto-validation enabled!
    fields:
      - username
      - email
      - age
  zData:
    action: insert
    table: users
    data: zConv
```

When `model: '@.zSchema.demo_users'` is specified:
1. ✅ zDialog loads the schema
2. ✅ Extracts validation rules for each field
3. ✅ Validates form data **before** `onSubmit`
4. ✅ Displays errors if validation fails (Terminal + zBifrost modes)
5. ✅ Only proceeds to `zData.insert` if validation passes

## 🏆 Benefits

- ✅ **Immediate feedback** - No wasted round-trips
- ✅ **Consistent validation** - Same rules in forms and database
- ✅ **Declarative** - No manual validation code needed
- ✅ **Dual-mode** - Works in Terminal AND zBifrost
- ✅ **Backward compatible** - Forms without `model:` work as before

## 📊 Test Coverage

This feature is tested with **12 comprehensive tests** in `zTestSuite/zDialog_AutoValidation_Test.py`:

- ✅ Valid data (should succeed)
- ✅ Invalid username pattern
- ✅ Invalid email format
- ✅ Age out of range
- ✅ Missing required fields
- ✅ Graceful fallback (no model, invalid model)
- ✅ WebSocket error broadcast (zBifrost mode)
- ✅ onSubmit integration

All **1113/1113 tests passing (100%)** 🎉

