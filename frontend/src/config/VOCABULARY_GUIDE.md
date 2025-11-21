# Voice Vocabulary & Accent Normalization Guide

## Overview

The voice assistant uses a vocabulary normalization system to improve speech recognition accuracy, especially for UPI commands and Indian accents. This system maps common misrecognitions and accent variations to correct terms.

## How It Works

1. **Speech Recognition**: The Web Speech API captures your voice input
2. **Normalization**: The transcript is normalized using vocabulary mappings and accent patterns
3. **Processing**: The normalized transcript is sent to the backend for processing

## Adding New Vocabulary

To add new vocabulary mappings or accent variations, edit `vocabularyConfig.js`:

### 1. Add Vocabulary Mappings

Add entries to `UPI_VOCABULARY` for your language:

```javascript
'en-IN': {
  // Add your mappings here
  'misrecognized term': 'correct term',
  'another variation': 'correct term',
}
```

### 2. Add Accent Patterns

Add regex patterns to `ACCENT_PATTERNS` for accent-specific variations:

```javascript
'en-IN': [
  {
    pattern: /\b(misrecognized|pattern)\b/gi,
    replacement: 'correct term'
  }
]
```

### 3. Add Common Phrases

Add complete phrases to `UPI_PHRASES` that users might say:

```javascript
'en-IN': [
  'your phrase here',
  'another common phrase',
]
```

## Examples

### Example 1: UPI Term Variations

If users often say "you pee" instead of "upi", add:

```javascript
'en-IN': {
  'you pee': 'upi',
  'you p i': 'upi',
}
```

### Example 2: Accent Variations

If Indian English speakers say "acount" instead of "account", add:

```javascript
'en-IN': [
  {
    pattern: /\b(acount|acounts)\b/gi,
    replacement: 'account'
  }
]
```

### Example 3: Hindi Variations

If Hindi speakers say "हेलो वानी" instead of "हेलो वाणी", add:

```javascript
'hi-IN': {
  'हेलो वानी': 'हेलो वाणी',
}
```

## Testing

After adding vocabulary:

1. Test with voice input in the chat interface
2. Check browser console logs to see:
   - Raw transcript
   - Normalized transcript
3. Verify that your variations are correctly normalized

## Current Coverage

### English (en-IN)
- UPI wake-up phrases ("hello vaani", "hello upi")
- UPI term variations ("you pee", "you p i")
- Payment terms ("pay", "send", "transfer")
- Amount terms ("rupees", "hundred", "thousand", "lakh")
- Beneficiary terms ("first", "last", "beneficiary")
- Account terms ("account", "balance")

### Hindi (hi-IN)
- UPI wake-up phrases ("हेलो वाणी", "हेलो यूपीआई")
- UPI term variations ("यू पी आई", "यूपी")
- Payment terms ("भेजें", "भुगतान", "ट्रांसफर")
- Amount terms ("रुपये", "सौ", "हज़ार", "लाख")
- Beneficiary terms ("पहला", "आखिरी", "लाभार्थी")
- Account terms ("खाता", "बैलेंस", "शेष")

## Best Practices

1. **Test with real users**: Collect common misrecognitions from user feedback
2. **Add variations gradually**: Don't add too many mappings at once
3. **Use regex for patterns**: For complex variations, use accent patterns
4. **Preserve case**: The system tries to preserve capitalization when possible
5. **Language-specific**: Always add mappings for the correct language code

## Troubleshooting

### Normalization not working?

1. Check browser console for normalization logs
2. Verify the language code matches your configuration
3. Ensure the mapping key exactly matches the misrecognized term
4. Check that the pattern regex is correct (for accent patterns)

### Still having issues?

1. Check the raw transcript in console logs
2. Add more specific mappings for your accent
3. Consider adding phrase-level mappings for multi-word phrases

