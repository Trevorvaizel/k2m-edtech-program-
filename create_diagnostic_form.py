#!/usr/bin/env python3
"""
K2M Diagnostic Form Creator
Automatically creates Google Forms diagnostic from Story 5.4 specification

Usage:
    python create_diagnostic_form.py

Requirements:
    - credentials.json in same directory (from Google Cloud Console)
    - pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

import os
import sys
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth

# Scopes for Google Forms API
SCOPES = ['https://www.googleapis.com/auth/forms.body']

# Try multiple possible credential filenames
CREDENTIALS_FILES = [
    'credentials.json',
    'client_secret_*.json'  # Auto-generated naming from Google Cloud Console
]


def authenticate():
    """Authenticate using credentials.json OR gcloud CLI credentials"""
    import glob
    creds = None

    # Method 1: Try to find any credential file
    creds_file = None
    for pattern in CREDENTIALS_FILES:
        matches = glob.glob(pattern)
        if matches:
            creds_file = matches[0]
            break

    if creds_file:
        print(f"🔐 Using {creds_file}...")
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
        creds = flow.run_local_server(port=0)

    # Method 2: Fall back to gcloud auth (if available)
    else:
        print("🔐 Using gcloud CLI authentication...")
        try:
            creds, project_id = google.auth.default(scopes=SCOPES)
        except Exception as e:
            print(f"❌ No credentials found!")
            print(f"\n💡 Solutions:")
            print(f"   1. Place any credentials.json file in this directory")
            print(f"   2. Or run: gcloud auth login")
            sys.exit(1)

    # Refresh if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    service = build('forms', 'v1', credentials=creds)
    print("✅ Authenticated successfully!")
    return service


def create_diagnostic_form(service):
    """Create the complete diagnostic form from Story 5.4 spec"""

    # Create new form
    form_info = {
        'info': {
            'title': 'K2M Cohort #X - Student Onboarding Diagnostic',
            'description': '''Welcome! This diagnostic helps us understand where you're starting from.

There are no right or wrong answers. Your honest responses help us support you.
This takes 10-15 minutes. All responses are confidential (Trevor only).

It's okay if you feel anxious about AI. Most students do.
You're in the right place.

---
**Privacy Assurance:**
- Your responses are CONFIDENTIAL - only Trevor sees them
- Data is stored securely in Google Sheets (encrypted)
- Data is deleted 6 months after cohort completion
- We NEVER share your responses with other students
- We NEVER sell your data to third parties
- Parent contact information is used ONLY for emergencies or weekly updates (your choice)

By submitting this form, you consent to this data use.
You can ask Trevor to delete your data anytime during the cohort.'''
        }
    }

    result = service.forms().create(body=form_info).execute()
    form_id = result['formId']
    form_url = result['responderUri']

    print(f"\n✅ Form created successfully!")
    print(f"Form ID: {form_id}")
    print(f"Form URL: {form_url}")
    print("\n⏳ Adding sections and questions...\n")

    # Track requests for batching
    requests = []

    # ========================================================================
    # SECTION 0: Age Verification (for minors consent)
    # ========================================================================
    print("📝 Adding Section 0: Age Verification...")

    age_request = {
        'createItem': {
            'item': {
                'title': 'How old are you?',
                'questionItem': {
                    'question': {
                        'required': True,
                        'choiceQuestion': {
                            'type': 'RADIO',
                            'options': [
                                {'value': '16 or under'},
                                {'value': '17'},
                                {'value': '18'},
                                {'value': '19 or over'}
                            ],
                            'shuffle': False
                        }
                    }
                }
            }
        }
    }
    requests.append(age_request)

    # ========================================================================
    # SECTION 1: Basic Information
    # ========================================================================
    print("📝 Adding Section 1: Basic Information...")

    # First Name
    requests.append({
        'createItem': {
            'item': {
                'title': 'First Name',
                'questionItem': {
                    'question': {
                        'required': True,
                        'textQuestion': {
                            'paragraph': False
                        }
                    }
                }
            }
        }
    })

    # Last Name (for cluster assignment)
    requests.append({
        'createItem': {
            'item': {
                'title': 'Last Name',
                'questionItem': {
                    'question': {
                        'required': True,
                        'textQuestion': {
                            'paragraph': False
                        }
                    }
                }
            }
        }
    })

    # Email Address
    requests.append({
        'createItem': {
            'item': {
                'title': 'Email Address',
                'questionItem': {
                    'question': {
                        'required': True,
                        'textQuestion': {
                            'paragraph': False
                        }
                    }
                }
            }
        }
    })

    # Discord Username (optional)
    requests.append({
        'createItem': {
            'item': {
                'title': 'Discord Username (optional - for matching)',
                'questionItem': {
                    'question': {
                        'required': False,
                        'textQuestion': {
                            'paragraph': False
                        }
                    }
                }
            }
        }
    })

    # ========================================================================
    # SECTION 2: Zone Self-Assessment
    # ========================================================================
    print("📝 Adding Section 2: Zone Assessment...")

    # Zone self-assessment (simple language - Guardrail #3 compliant)
    requests.append({
        'createItem': {
            'item': {
                'title': 'Where are you starting from with AI?',
                'description': 'Self-identify - no right or wrong answer',
                'questionItem': {
                    'question': {
                        'required': True,
                        'choiceQuestion': {
                            'type': 'RADIO',
                            'options': [
                                {
                                    'value': '"AI is not for me / it\'s sci-fi"',
                                    'isOther': False
                                },
                                {
                                    'value': '"AI is something I could use"',
                                    'isOther': False
                                },
                                {
                                    'value': '"AI does tasks for me"',
                                    'isOther': False
                                },
                                {
                                    'value': '"AI understands my intent / I collaborate with it"',
                                    'isOther': False
                                },
                                {
                                    'value': '"I control quality / I direct AI"',
                                    'isOther': False
                                }
                            ],
                            'shuffle': False
                        }
                    }
                }
            }
        }
    })

    # Zone verification (scenario-based - prevents overestimation)
    requests.append({
        'createItem': {
            'item': {
                'title': 'Which scenario sounds MOST like you?',
                'description': 'This helps verify your self-assessment (no judgment)',
                'questionItem': {
                    'question': {
                        'required': True,
                        'choiceQuestion': {
                            'type': 'RADIO',
                            'options': [
                                {
                                    'value': '"I wouldn\'t know where to start. I\'d ask a friend or just do it myself."',
                                    'isOther': False
                                },
                                {
                                    'value': '"I\'d open ChatGPT and type \'help me with [topic].\'"',
                                    'isOther': False
                                },
                                {
                                    'value': '"I\'d open ChatGPT and explain: \'I\'m working on [assignment], here\'s what I know so far...\'"',
                                    'isOther': False
                                },
                                {
                                    'value': '"I\'d have a back-and-forth conversation: \'Here\'s my situation. What do you think? Okay, now let\'s try this...\'"',
                                    'isOther': False
                                },
                                {
                                    'value': '"I\'d direct it: \'Draft me three options for [topic]. Now make the second one more specific to my situation.\'"',
                                    'isOther': False
                                }
                            ],
                            'shuffle': False
                        }
                    }
                }
            }
        }
    })

    # AI Experience Level
    requests.append({
        'createItem': {
            'item': {
                'title': 'AI Experience Level',
                'questionItem': {
                    'question': {
                        'required': True,
                        'choiceQuestion': {
                            'type': 'RADIO',
                            'options': [
                                {'value': 'Never used', 'isOther': False},
                                {'value': 'Tried a few times', 'isOther': False},
                                {'value': 'Use regularly', 'isOther': False},
                                {'value': 'Use daily', 'isOther': False}
                            ],
                            'shuffle': False
                        }
                    }
                }
            }
        }
    })

    # ========================================================================
    # SECTION 3: Emotional Baseline (ALL OPTIONAL - Guardrail #3)
    # ========================================================================
    print("📝 Adding Section 3: Emotional Baseline (all optional)...")

    # How are you feeling? (checkboxes)
    requests.append({
        'createItem': {
            'item': {
                'title': 'How are you feeling about AI right now?',
                'description': 'Check all that apply - or skip if you prefer',
                'questionItem': {
                    'question': {
                        'required': False,
                        'choiceQuestion': {
                            'type': 'CHECKBOX',
                            'options': [
                                {'value': 'Curious'},
                                {'value': 'Anxious'},
                                {'value': 'Excited'},
                                {'value': 'Overwhelmed'},
                                {'value': 'Confused'},
                                {'value': 'Hopeful'},
                                {'value': 'Other (please specify)', 'isOther': True}
                            ],
                            'shuffle': False
                        }
                    }
                }
            }
        }
    })

    # Anxiety level (1-10 scale)
    requests.append({
        'createItem': {
            'item': {
                'title': 'On a scale of 1-10, how anxious do you feel about AI?',
                'description': '1 = "Calm, not worried" | 5 = "Nervous but manageable" | 10 = "Panicked, avoiding AI entirely"',
                'questionItem': {
                    'question': {
                        'required': False,
                        'scaleQuestion': {
                            'minimum': 1,
                            'maximum': 10,
                            'low': 'Not at all anxious',
                            'high': 'Extremely anxious'
                        }
                    }
                }
            }
        }
    })

    # Confidence level
    requests.append({
        'createItem': {
            'item': {
                'title': 'How confident do you feel about your understanding of AI right now?',
                'description': 'This helps us support you better (optional)',
                'questionItem': {
                    'question': {
                        'required': False,
                        'choiceQuestion': {
                            'type': 'RADIO',
                            'options': [
                                {'value': 'Not at all confident (I feel like I\'m missing something basic)'},
                                {'value': 'Somewhat confident (I\'m starting to get it, but not completely)'},
                                {'value': 'Fairly confident (I understand the basics)'},
                                {'value': 'Very confident (I feel solid on this)'},
                                {'value': 'I haven\'t thought about it'}
                            ],
                            'shuffle': False
                        }
                    }
                }
            }
        }
    })

    # Motivation (free text)
    requests.append({
        'createItem': {
            'item': {
                'title': 'What brings you to this cohort?',
                'description': 'E.g., "I\'m starting university soon and want to feel more confident with AI" or "My parents suggested this and I\'m curious"',
                'questionItem': {
                    'question': {
                        'required': False,
                        'textQuestion': {
                            'paragraph': True
                        }
                    }
                }
            }
        }
    })

    # Goals (free text)
    requests.append({
        'createItem': {
            'item': {
                'title': 'What do you hope to achieve by the end of Week 8?',
                'description': 'E.g., "Feel confident using AI for university assignments" or "Stop feeling like everyone else is ahead of me"',
                'questionItem': {
                    'question': {
                        'required': False,
                        'textQuestion': {
                            'paragraph': True
                        }
                    }
                }
            }
        }
    })

    # Optional vulnerability space
    requests.append({
        'createItem': {
            'item': {
                'title': 'Is there anything else we should know to support you?',
                'description': 'Optional: Share anything that would help us make this work better for you (learning style, schedule constraints, access needs, etc.)',
                'questionItem': {
                    'question': {
                        'required': False,
                        'textQuestion': {
                            'paragraph': True
                        }
                    }
                }
            }
        }
    })

    # 4 Habits Pre-Assessment (confidence builder)
    requests.append({
        'createItem': {
            'item': {
                'title': 'Which of these thinking habits do you ALREADY use?',
                'description': 'Check all that apply (or "None of these yet" - that\'s totally okay!)',
                'questionItem': {
                    'question': {
                        'required': False,
                        'choiceQuestion': {
                            'type': 'CHECKBOX',
                            'options': [
                                {'value': '⏸️ Pause before asking (I think about what I want before I open AI)'},
                                {'value': '🎯 Explain context first (I give AI background information)'},
                                {'value': '🔄 Change one thing at a time (I test small changes to see what works)'},
                                {'value': '🧠 Use AI before decisions (I ask AI to help me think through choices)'},
                                {'value': 'None of these yet (that\'s totally okay!)'}
                            ],
                            'shuffle': False
                        }
                    }
                }
            }
        }
    })

    # Kenya Crisis Resources (always show)
    requests.append({
        'createItem': {
            'item': {
                'title': '',
                'description': '''**Kenya Crisis Resources:**

If you're going through a difficult time, these resources are here to help:
- Befriending Kenya: +254 722 178 177 (free, confidential)
- Mental Health Kenya: +254 733 111 000
- Youth Crisis Hotline: +254 1199
- Emergency: 999 or 112

You can always DM Trevor if you need support.'''
            }
        }
    })

    # ========================================================================
    # SECTION 4: Parent/Guardian Contact Information (REQUIRED - Level 4 Crisis)
    # ========================================================================
    print("📝 Adding Section 4: Parent/Guardian Contact (required)...")

    # Parent/Guardian Name
    requests.append({
        'createItem': {
            'item': {
                'title': 'Parent/Guardian Full Name',
                'description': 'Required for crisis intervention support',
                'questionItem': {
                    'question': {
                        'required': True,
                        'textQuestion': {
                            'paragraph': False
                        }
                    }
                }
            }
        }
    })

    # Parent/Guardian Phone Number
    requests.append({
        'createItem': {
            'item': {
                'title': 'Parent/Guardian Phone Number',
                'description': 'Required format: e.g., 254700000000 or +1234567890 (include country code if outside Kenya)',
                'questionItem': {
                    'question': {
                        'required': True,
                        'textQuestion': {
                            'paragraph': False
                        }
                    }
                }
            }
        }
    })

    # Parent/Guardian Email Address
    requests.append({
        'createItem': {
            'item': {
                'title': 'Parent/Guardian Email Address',
                'questionItem': {
                    'question': {
                        'required': True,
                        'textQuestion': {
                            'paragraph': False
                        }
                    }
                }
            }
        }
    })

    # Emergency Contact Backup (optional)
    requests.append({
        'createItem': {
            'item': {
                'title': 'Emergency Contact Backup (Optional)',
                'description': 'Alternative phone number if we can\'t reach parent/guardian in an emergency',
                'questionItem': {
                    'question': {
                        'required': False,
                        'textQuestion': {
                            'paragraph': False
                        }
                    }
                }
            }
        }
    })

    # Crisis Protocol Explanation
    requests.append({
        'createItem': {
            'item': {
                'title': '',
                'description': '''**When would we contact your parent/guardian?**
- If you're going through a really hard time and need support
- If we can't reach you and are worried about your safety
- We will NEVER contact your parent for academic performance, participation, or progress

If you're struggling, you can always reach out to Trevor directly.
You're not alone - we're here to support you.'''
            }
        }
    })

    # ========================================================================
    # SECTION 5: Weekly Updates Consent
    # ========================================================================
    print("📝 Adding Section 5: Weekly Updates Preference...")

    requests.append({
        'createItem': {
            'item': {
                'title': 'Weekly Progress Updates to Parents',
                'description': '''Would you like your parents to receive weekly email updates about your progress?

This is YOUR choice. You can change it anytime by DMing Trevor.
No pressure either way - both choices are completely okay.''',
                'questionItem': {
                    'question': {
                        'required': False,
                        'choiceQuestion': {
                            'type': 'RADIO',
                            'options': [
                                {
                                    'value': '✅ "Yes, send weekly updates"',
                                    'isOther': False
                                },
                                {
                                    'value': '❌ "No, keep it private until Week 8"',
                                    'isOther': False
                                },
                                {
                                    'value': '"I\'m not sure yet (I\'ll tell Trevor later)"',
                                    'isOther': False
                                }
                            ],
                            'shuffle': False
                        }
                    }
                }
            }
        }
    })

    # Weekly updates explanation
    requests.append({
        'createItem': {
            'item': {
                'title': '',
                'description': '''**If you choose "Yes":**
What we share (every Friday):
- "🌟 [Student] practiced Habit 1 (Pause) this week"
- "Posted reflections showing growth from 'confused' to 'getting it'"
- Celebrating thinking growth, never comparing to other students

What we NEVER share:
- Private DM conversations with CIS agents
- Your reflection details (only aggregate patterns)
- Any comparison to other students

**If you choose "No":**
- No updates until Week 8 artifact showcase
- At Week 8: Parents receive invitation to see your published artifact (your choice)
- Privacy honored throughout the cohort'''
            }
        }
    })

    # ========================================================================
    # BATCH ALL REQUESTS
    # ========================================================================
    print(f"\n⏳ Sending {len(requests)} questions to Google Forms API...")

    # Google Forms API batch limit is around 100 requests per batch
    # We'll send in smaller batches for reliability
    BATCH_SIZE = 50
    for i in range(0, len(requests), BATCH_SIZE):
        batch = requests[i:i+BATCH_SIZE]
        batch_request = {'requests': batch}

        update_result = service.forms().batchUpdate(
            formId=form_id,
            body=batch_request
        ).execute()

        print(f"✅ Sent batch {i//BATCH_SIZE + 1}/{(len(requests)-1)//BATCH_SIZE + 1}")

    print("\n✅ All sections and questions added successfully!")

    return form_id, form_url


def main():
    """Main execution"""
    print("=" * 60)
    print("K2M Diagnostic Form Creator")
    print("=" * 60)
    print("\n🔐 Authenticating...")

    try:
        service = authenticate()
        print("✅ Authenticated successfully!\n")

        form_id, form_url = create_diagnostic_form(service)

        print("\n" + "=" * 60)
        print("SUCCESS! Form Created")
        print("=" * 60)
        print(f"\n📋 Form ID: {form_id}")
        print(f"\n🔗 Form URL (for students):")
        print(f"   {form_url}")
        print(f"\n📝 Google Forms Editor (for manual tweaks):")
        print(f"   https://docs.google.com/forms/d/{form_id}/edit")
        print(f"\n✅ Next Steps:")
        print(f"   1. Test the form: {form_url}")
        print(f"   2. Make any manual adjustments in Google Forms editor")
        print(f"   3. Copy the URL to your landing page")
        print(f"   4. Connect to Google Sheets (can be done manually)")
        print(f"\n💡 Tip: Your gcloud auth is all you need for future automation!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you ran: gcloud auth login")
        print("2. Check project is set: gcloud config list project")
        print("3. Enable Forms API: gcloud services enable forms.googleapis.com")
        print("4. Verify active account: gcloud auth list")
        sys.exit(1)


if __name__ == '__main__':
    main()
