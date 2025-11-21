# Voice Vocabulary & Accent Normalization Feature

## Overview

This feature adds vocabulary teaching and accent normalization capabilities to the voice assistant, specifically optimized for UPI commands and Indian accents. The system automatically normalizes speech recognition transcripts to improve accuracy for hands-free voice mode.

## What Was Implemented

### 1. Vocabulary Configuration System (`frontend/src/config/vocabularyConfig.js`)

A comprehensive vocabulary mapping system that includes:

- **UPI-specific vocabulary mappings**: Maps common misrecognitions to correct UPI terms
- **Accent pattern normalization**: Regex-based patterns to handle accent variations
- **Language-specific support**: Separate configurations for English (en-IN) and Hindi (hi-IN)
- **Common phrase recognition**: Predefined phrases for UPI commands

### 2. Speech Recognition Integration

The normalization is automatically applied in `useSpeechRecognition` hook:

- Raw transcripts from Web Speech API are normalized before being displayed
- Both interim and final transcripts are normalized
- Normalization logs are available in browser console for debugging

### 3. Features

#### English (en-IN) Support

- **Wake-up phrases**: "hello vaani", "hello upi" variations
- **UPI terms**: "you pee", "you p i", "you pie" → "upi"
- **Payment terms**: "pay", "send", "transfer" variations
- **Amount terms**: "rupees", "hundred", "thousand", "lakh" variations
- **Account terms**: "account", "balance" variations
- **Beneficiary terms**: "first", "last", "beneficiary" variations

#### Hindi (hi-IN) Support

- **Wake-up phrases**: "हेलो वाणी", "हेलो यूपीआई" variations
- **UPI terms**: "यू पी आई", "यूपी" → "यूपीआई"
- **Payment terms**: "भेजें", "भुगतान", "ट्रांसफर" variations
- **Amount terms**: "रुपये", "सौ", "हज़ार", "लाख" variations
- **Account terms**: "खाता", "बैलेंस", "शेष" variations

## How It Works

1. **User speaks**: Voice input is captured by Web Speech API
2. **Raw transcript**: Initial transcript may contain misrecognitions
3. **Normalization**: 
   - Accent patterns are applied (regex replacements)
   - Vocabulary mappings are applied (exact word/phrase matches)
   - Phrase-level mappings are applied (multi-word phrases)
4. **Normalized transcript**: Corrected transcript is displayed and sent to backend

## Example Normalizations

### Example 1: UPI Term
- **Raw**: "hello vanni, pay hundred rupees via you pee"
- **Normalized**: "hello vaani, pay hundred rupees via upi"

### Example 2: Account Term
- **Raw**: "check balance of acount ending with four four"
- **Normalized**: "check balance of account ending with four four"

### Example 3: Hindi Variation
- **Raw**: "हेलो वानी, यू पी आई भुगतान करें"
- **Normalized**: "हेलो वाणी, यूपीआई भुगतान करें"

## Adding New Vocabulary

See `frontend/src/config/VOCABULARY_GUIDE.md` for detailed instructions on:

- Adding vocabulary mappings
- Adding accent patterns
- Adding common phrases
- Testing new vocabulary
- Troubleshooting

## Benefits

1. **Improved Accuracy**: Reduces misrecognitions for UPI-specific terms
2. **Accent Tolerance**: Handles variations in Indian English and Hindi accents
3. **Better UX**: Users don't need to speak perfectly - common variations are handled
4. **Extensible**: Easy to add new vocabulary and patterns
5. **Language Support**: Works for both English and Hindi

## Technical Details

- **Location**: `frontend/src/config/vocabularyConfig.js`
- **Integration**: `frontend/src/hooks/useSpeechRecognition.js`
- **Language Support**: en-IN, hi-IN (extensible to other languages)
- **Normalization**: Applied in real-time during speech recognition

## Testing

To test the vocabulary normalization:

1. Open the chat interface in voice mode
2. Speak UPI commands with variations (e.g., "hello vanni" instead of "hello vaani")
3. Check browser console for normalization logs:
   - Raw transcript
   - Normalized transcript
4. Verify that commands are correctly recognized

## Future Enhancements

Potential improvements:

1. **User-specific vocabulary**: Learn from user corrections
2. **Regional accent profiles**: Pre-configured profiles for different regions
3. **Dynamic learning**: Automatically add common misrecognitions
4. **More languages**: Extend to Tamil, Telugu, and other Indian languages
5. **Context-aware normalization**: Different mappings based on conversation context

## Related Files

- `frontend/src/config/vocabularyConfig.js` - Vocabulary configuration
- `frontend/src/config/VOCABULARY_GUIDE.md` - User guide for adding vocabulary
- `frontend/src/hooks/useSpeechRecognition.js` - Speech recognition hook with normalization
- `frontend/src/config/voiceConfig.js` - Voice configuration (language settings)

