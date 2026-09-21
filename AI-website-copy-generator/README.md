# AI Website Copy Generator for Local Businesses

Prompt templates for writing website copy for small local businesses: a salon, a café, a clinic, a small digital agency. You fill in the business details once, and the script gives you a ready-to-paste prompt for a homepage, a service page or call-to-action buttons.

## Why I made this

Ask an AI to "write website copy for my salon" and you usually get the same glossy paragraph every time, full of words no shop owner would say out loud. Sometimes it also makes up prices, awards or "10 years of experience" that the business never had. That's a real problem for a local business.

So these prompts are strict about a few things:

- **Only use the facts given.** No invented prices, awards, testimonials or statistics.
- **Leave a gap instead of guessing.** If a detail is missing, the output has an `[ADD: ...]` tag so the owner can fill it in.
- **Sound like a person.** Short sentences, everyday words, and a list of overused phrases the model isn't allowed to use.
- **Respect the business.** Each business file can carry its own rules (for example, the clinic one bans medical claims and fear-based urgency).

## What's inside

```
.
├── generate_prompt.py        # fills a template with a business's details
├── prompts/
│   ├── homepage.md           # hero, intro, services, why us, closing CTA
│   ├── service_page.md       # title, meta description, H1, FAQ for one service
│   └── cta.md                # button + supporting line for 4 placements
├── businesses/
│   ├── salon.json
│   ├── cafe.json
│   ├── clinic.json
│   ├── digital_agency.json
│   └── _template.json        # copy this to add your own
├── examples/                 # what the output looks like
├── tests/
└── LICENSE
```

The four businesses are made up. They're only there to show the templates working.

## Quick start

You need Python 3.8 or newer. There's nothing to install.

```bash
# see what's available
python generate_prompt.py --list

# print a homepage prompt for the salon
python generate_prompt.py -b salon -t homepage

# a service page for one specific service
python generate_prompt.py -b cafe -t service_page -s "Small event bookings"

# save the prompt into an output/ folder
python generate_prompt.py -b clinic -t cta --save
```

Copy the printed prompt into ChatGPT, Gemini, Claude or any other chatbot and you'll get the copy back.

You can also skip the script completely. Every file in `prompts/` is plain text: copy it, replace the `{{placeholders}}` by hand and paste it in.

## Running it straight through Gemini (optional)

If you have a Gemini API key (you can get one from Google AI Studio), the script can send the prompt for you:

```bash
export GEMINI_API_KEY="your-key-here"      # on Windows: set GEMINI_API_KEY=your-key-here
python generate_prompt.py -b salon -t homepage --run --save
```

It calls the Gemini REST API using only Python's standard library. The default model is `gemini-2.5-flash`; set `GEMINI_MODEL` to use a different one. With `--save`, both the prompt and the result go into `output/` (which is git-ignored).

## Add your own business

1. Copy `businesses/_template.json` to something like `businesses/bakery.json`.
2. Fill in the fields:

| Field | What to put |
|---|---|
| `business_name` | Name as it should appear on the site |
| `business_type` | For example "Women's salon" or "Family clinic" |
| `city` | Where the business is |
| `target_audience` | Who the customers are, in a sentence |
| `services` | A list of services |
| `unique_selling_points` | A list of real things that set them apart. Only facts you're sure about |
| `tone` | How it should sound |
| `primary_action` | The one thing a visitor should do (book, call, visit) |
| `extra_rules` | Business-specific do's and don'ts, or `"None"` |

3. Run `python generate_prompt.py -b bakery -t homepage`.

The quality of the copy depends on the quality of these details. Vague input gives vague copy.

## Examples

Look in [`examples/`](examples/) to see the kind of output the prompts produce:

- [Salon homepage](examples/salon_homepage.md)
- [Café service page](examples/cafe_service_page.md) (shows the `[ADD: ...]` tags)
- [Clinic CTA options](examples/clinic_cta.md)
- [Digital agency homepage](examples/digital_agency_homepage.md)

## Tests

```bash
python -m unittest discover -s tests
```

The tests check that every business fills every template with nothing left over, and that a missing field gives a clear error.

## Limits and what I'd like to add

- The sample businesses are made up, so the copy hasn't been checked by a real owner yet.
- English only for now. A Hindi version of the prompts would be useful for local businesses.
- More templates: About page, Google Business Profile description, WhatsApp welcome message.
- A small web form so a shop owner could fill in the details without touching JSON.

## License

MIT. See [LICENSE](LICENSE).
