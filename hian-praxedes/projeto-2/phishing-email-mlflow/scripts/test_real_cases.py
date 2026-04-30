import requests
from collections import Counter

URL = "http://127.0.0.1:5001/invocations"

# Convenção inferida dos seus testes:
# LABEL_0 = legitimate / safe
# LABEL_1 = phishing

cases = [
    # =========================================================
    # SAFE CORPORATE / ENRON-LIKE
    # =========================================================
    {
        "name": "safe_corporate_1_ticket_setup",
        "group": "safe_corporate",
        "expected": "LABEL_0",
        "text": (
            "Subject: Re: Equistar deal tickets\n\n"
            "Are you still available to assist Robert with entering the new deal tickets for Equistar? "
            "After talking with Bryan Hull and Anita Luong, Kyle and I decided that we only need one "
            "additional sale ticket and one additional buyback ticket set up. Please let me know if "
            "there are any issues with the pricing assumptions."
        ),
    },
    {
        "name": "safe_corporate_2_internal_followup",
        "group": "safe_corporate",
        "expected": "LABEL_0",
        "text": (
            "Subject: Updated schedule for tomorrow\n\n"
            "Hello team, please review the updated meeting schedule before 5 PM. "
            "The room assignment changed and the attached document reflects the latest agenda. "
            "If you see any conflict with your calendar, let me know directly."
        ),
    },
    {
        "name": "safe_corporate_3_finance_review",
        "group": "safe_corporate",
        "expected": "LABEL_0",
        "text": (
            "Subject: March invoice and reconciliation\n\n"
            "Hi John, attached is the March invoice together with the reconciliation sheet. "
            "Please review the line items and confirm whether the billing address and cost center "
            "still match last month's record."
        ),
    },
    {
        "name": "safe_corporate_4_it_maintenance",
        "group": "safe_corporate",
        "expected": "LABEL_0",
        "text": (
            "Subject: Scheduled maintenance tonight\n\n"
            "Good afternoon, the IT team will perform scheduled maintenance tonight from 10 PM to 11 PM. "
            "Some internal systems may be temporarily unavailable during this period. "
            "No user action is required."
        ),
    },

    # =========================================================
    # SAFE WEIRD HAM
    # Imitando o estilo estranho de listas, discussões e textos esquisitos
    # =========================================================
    {
        "name": "safe_weird_ham_1_linguistics_list",
        "group": "safe_weird_ham",
        "expected": "LABEL_0",
        "text": (
            "Subject: Re: daughter and son as vocatives\n\n"
            "Dick Hudson's observation about the use of 'son' but not 'daughter' as a vocative is very "
            "thought-provoking, though I am not sure that it is fair to attribute this directly to seniority. "
            "For one thing, we do not normally use 'brother' in the same way, which complicates the comparison."
        ),
    },
    {
        "name": "safe_weird_ham_2_language_question",
        "group": "safe_weird_ham",
        "expected": "LABEL_0",
        "text": (
            "Subject: The other side of galicismos\n\n"
            "Galicismo is a Spanish term used for improper introduction of French words into Spanish. "
            "What would be the corresponding term for unlawful words of Spanish origin that may have "
            "crept into French? Can anyone provide examples?"
        ),
    },
    {
        "name": "safe_weird_ham_3_mailing_list_reply",
        "group": "safe_weird_ham",
        "expected": "LABEL_0",
        "text": (
            "Subject: Re: workshop bibliography\n\n"
            "Thanks for the references. I checked the bibliography you sent and I think the second paper "
            "may be more relevant than the first for the session on discourse markers. "
            "I will bring a printed copy tomorrow."
        ),
    },
    {
        "name": "safe_weird_ham_4_internal_note_unusual_style",
        "group": "safe_weird_ham",
        "expected": "LABEL_0",
        "text": (
            "Subject: Notes from the archive room\n\n"
            "I found the missing folder behind the old shelf in the archive room. "
            "It contains the revised copy as well as a handwritten note from the prior review cycle. "
            "Please do not discard anything until we reconcile the index."
        ),
    },

    # =========================================================
    # PHISHING / SPAM CLARO
    # Mais alinhado com spam de baixa qualidade presente no dataset
    # =========================================================
    {
        "name": "phishing_spam_1_adult_phone",
        "group": "phishing_spam",
        "expected": "LABEL_1",
        "text": (
            "Hello I am your hot little secret fantasy. "
            "I am open minded and ready right now. "
            "Call me immediately and make your dreams come true. "
            "TOLL FREE number available now for private late night fun."
        ),
    },
    {
        "name": "phishing_spam_2_discount_software",
        "group": "phishing_spam",
        "expected": "LABEL_1",
        "text": (
            "Software at incredibly low prices, up to 86 percent lower than retail. "
            "Order now, special deal, famous products, no prescription, fast delivery, "
            "limited time only and immediate savings for smart buyers."
        ),
    },
    {
        "name": "phishing_spam_3_pharma_style",
        "group": "phishing_spam",
        "expected": "LABEL_1",
        "text": (
            "Cheap quality medication available online now. "
            "Private shipping, huge discounts, no waiting, no extra paperwork, "
            "exclusive customer offer available today only."
        ),
    },
    {
        "name": "phishing_spam_4_urgent_verification",
        "group": "phishing_spam",
        "expected": "LABEL_1",
        "text": (
            "Dear user, your account has been suspended due to unusual activity. "
            "Verify your credentials immediately using the secure link below to restore access."
        ),
    },

    # =========================================================
    # STOCK / INVESTMENT SPAM
    # Bem parecido com pump-and-dump / newsletter agressiva
    # =========================================================
    {
        "name": "phishing_stock_1_biotech_gain",
        "group": "phishing_stock",
        "expected": "LABEL_1",
        "text": (
            "Entourage Stock Newsletter: tiny biotech opportunity with explosive earnings potential. "
            "Revenue is growing fast, early investors may see extraordinary gains, and this underpriced company "
            "could multiply in value within days. Act before Wall Street notices."
        ),
    },
    {
        "name": "phishing_stock_2_microcap_alert",
        "group": "phishing_stock",
        "expected": "LABEL_1",
        "text": (
            "Microcap alert: ordinary investors are getting rich from hidden small cap stocks before the market "
            "catches up. Our analysts believe this symbol is positioned for a major breakout. "
            "Do not miss this window."
        ),
    },
    {
        "name": "phishing_stock_3_penny_stock",
        "group": "phishing_stock",
        "expected": "LABEL_1",
        "text": (
            "Insider-style alert for aggressive investors: this low-float company could move 300 percent "
            "or more after the next announcement. Join the early buying wave now and profit from the momentum."
        ),
    },
    {
        "name": "phishing_stock_4_fake_newsletter",
        "group": "phishing_stock",
        "expected": "LABEL_1",
        "text": (
            "Special investor bulletin: our featured company is rapidly expanding across international markets "
            "and may deliver exceptional upside. Subscribe now for the next symbol before publication."
        ),
    },

    # =========================================================
    # PHISHING MISTURADO EM TEXTO PROFISSIONAL
    # Esse é o grupo mais importante para estressar o modelo
    # =========================================================
    {
        "name": "phishing_mixed_1_finance_report",
        "group": "phishing_mixed_professional",
        "expected": "LABEL_1",
        "text": (
            "Hello team, please review the updated finance report for Q1 before tomorrow's meeting. "
            "Also, due to a recent security update, all employees must confirm their mailbox credentials today "
            "using the secure form below to avoid interruption of access."
        ),
    },
    {
        "name": "phishing_mixed_2_hr_policy",
        "group": "phishing_mixed_professional",
        "expected": "LABEL_1",
        "text": (
            "Dear employee, HR has shared the revised remote work policy and requests that everyone read it "
            "before Friday. In addition, your employee portal session has expired, so please log in again using "
            "the verification link below to prevent account suspension."
        ),
    },
    {
        "name": "phishing_mixed_3_client_presentation",
        "group": "phishing_mixed_professional",
        "expected": "LABEL_1",
        "text": (
            "Good afternoon, the client presentation draft has been uploaded for your review and comments. "
            "Because the document contains restricted content, you must re-enter your corporate email password "
            "to access the file securely."
        ),
    },
    {
        "name": "phishing_mixed_4_invoice_followup",
        "group": "phishing_mixed_professional",
        "expected": "LABEL_1",
        "text": (
            "Hi John, following our previous conversation, I am sending the invoice and payment summary for March. "
            "Before opening the attachment, please confirm your identity through the secure login page below "
            "due to new anti-fraud measures."
        ),
    },

    # =========================================================
    # SPEAR PHISHING MAIS PROFISSIONAL
    # =========================================================
    {
        "name": "phishing_spear_1_manager_request",
        "group": "phishing_spear",
        "expected": "LABEL_1",
        "text": (
            "Hi Maria, I am traveling today and need you to urgently review the attached board document. "
            "The file is protected because it contains salary adjustments, so please sign in with your "
            "corporate email and password when prompted to view it."
        ),
    },
    {
        "name": "phishing_spear_2_vendor_invoice",
        "group": "phishing_spear",
        "expected": "LABEL_1",
        "text": (
            "Good morning, attached is the revised supplier invoice and tax summary requested for closing. "
            "Because our finance system recently changed, please validate your account credentials on the secure "
            "billing page below before processing the document."
        ),
    },
    {
        "name": "phishing_spear_3_legal_review",
        "group": "phishing_spear",
        "expected": "LABEL_1",
        "text": (
            "Dear Counsel, the opposing party has submitted an updated filing for your review. "
            "Due to confidentiality restrictions, access requires immediate mailbox verification "
            "through the secure legal review portal."
        ),
    },
    {
        "name": "phishing_spear_4_benefits_enrollment",
        "group": "phishing_spear",
        "expected": "LABEL_1",
        "text": (
            "Open enrollment closes this evening, and your benefits selection is still incomplete. "
            "To finalize your record, sign in now through the employee benefits confirmation page below "
            "using your usual corporate credentials."
        ),
    },

    # =========================================================
    # AMBÍGUOS / BORDERLINE
    # Alguns deveriam ser legítimos, outros phishing.
    # Aqui a intenção é realmente fazer o modelo sofrer.
    # =========================================================
    {
        "name": "ambiguous_1_official_portal_notice_legit",
        "group": "ambiguous_borderline",
        "expected": "LABEL_0",
        "text": (
            "The security office reminds employees to complete mandatory account verification this month "
            "through the official employee portal listed on the intranet homepage. "
            "No action is required through this email."
        ),
    },
    {
        "name": "ambiguous_2_fake_it_phishing",
        "group": "ambiguous_borderline",
        "expected": "LABEL_1",
        "text": (
            "The IT department detected an issue with your account. Sign in now using your email password "
            "to prevent access suspension and restore synchronization."
        ),
    },
    {
        "name": "ambiguous_3_shared_workspace_legit",
        "group": "ambiguous_borderline",
        "expected": "LABEL_0",
        "text": (
            "A new draft document is available in the shared workspace. "
            "Access it through the normal collaboration portal after signing in the usual way."
        ),
    },
    {
        "name": "ambiguous_4_secure_viewer_phishing",
        "group": "ambiguous_borderline",
        "expected": "LABEL_1",
        "text": (
            "A secure shared document is waiting for you. To open it, re-enter your email credentials now "
            "through the protected viewer below."
        ),
    },
    {
        "name": "ambiguous_5_helpdesk_legit",
        "group": "ambiguous_borderline",
        "expected": "LABEL_0",
        "text": (
            "Support ticket 48321 has been updated. Please log into the official helpdesk portal when convenient "
            "to review the technician response."
        ),
    },
    {
        "name": "ambiguous_6_helpdesk_phishing",
        "group": "ambiguous_borderline",
        "expected": "LABEL_1",
        "text": (
            "Support ticket 48321 requires immediate account confirmation. "
            "Please validate your credentials now through the support recovery page to avoid closure."
        ),
    },
]

def predict(text: str):
    payload = {"dataframe_records": [{"text": text}]}
    response = requests.post(URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    pred = data["predictions"][0]["label"]
    score = data["predictions"][0]["score"]
    return pred, score

def main():
    correct = 0
    by_group_total = Counter()
    by_group_correct = Counter()

    for case in cases:
        by_group_total[case["group"]] += 1

        pred, score = predict(case["text"])
        ok = pred == case["expected"]

        if ok:
            correct += 1
            by_group_correct[case["group"]] += 1

        print("-" * 100)
        print(f"CASE:      {case['name']}")
        print(f"GROUP:     {case['group']}")
        print(f"EXPECTED:  {case['expected']}")
        print(f"PREDICTED: {pred}")
        print(f"SCORE:     {score:.4f}")
        print(f"RESULT:    {'OK' if ok else 'WRONG'}")
        print("TEXT:")
        print(case["text"])
        print()

    total = len(cases)
    accuracy = correct / total if total else 0

    print("=" * 100)
    print(f"FINAL SCORE: {correct}/{total}")
    print(f"ACCURACY:    {accuracy:.2%}")
    print()

    print("BREAKDOWN BY GROUP:")
    for group in by_group_total:
        g_total = by_group_total[group]
        g_correct = by_group_correct[group]
        g_acc = g_correct / g_total if g_total else 0
        print(f"- {group}: {g_correct}/{g_total} ({g_acc:.2%})")

if __name__ == "__main__":
    main()