const lessonInteractions = {
  'java-spring-lld/oop-foundations/01-intro-to-lld': {
    conceptChecks: [
      {
        id: 'lesson-1-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01',
        question:
          'A client retries the same quote request with the same request ID. Which boundary should ensure the retry returns the original quote instead of starting a second negotiation?',
        options: [
          { id: 'a', label: 'A', text: 'The controller should calculate the fare and cache the HTTP response.' },
          { id: 'b', label: 'B', text: 'The application boundary should remember the request ID and return the existing immutable quote.' },
          { id: 'c', label: 'C', text: 'The distance provider should decide whether a quote has already been negotiated.' },
          { id: 'd', label: 'D', text: 'The pricing policy should mutate the previous quote before applying the fare again.' }
        ],
        correctOptionId: 'b',
        explanation:
          'QuoteService is the use-case boundary that owns idempotency. It can return the same immutable Quote for a repeated request ID while keeping transport, routing, distance lookup, and fare calculation in their own responsibilities.',
        incorrectExplanation:
          'Look for the boundary that coordinates the use case. Idempotency belongs where the request is interpreted and the quote is created, not in the controller, provider adapter, or pricing algorithm.',
        hint: 'request ID → QuoteService → immutable Quote',
        initialSelectedOption: 'b',
        initialSubmitted: true
      }
    ],
    architecture: {
      id: 'lesson-1-quote-service-flow',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — RIDE-BOOKING QUOTE SERVICE',
      boundaryLabel: 'BOUNDARY ACCEPTED',
      boundaryText:
        'QuoteService depends on distance and pricing capabilities, not on the infrastructure that supplies them.',
      nodes: [
        { id: 'request', label: 'Request', kind: 'input' },
        { id: 'controller', label: 'QuoteController', kind: 'service' },
        { id: 'service', label: 'QuoteService', kind: 'boundary', highlighted: true },
        { id: 'distance', label: 'DistanceProvider', kind: 'adapter' },
        { id: 'pricing', label: 'PricingPolicy', kind: 'adapter' },
        { id: 'quote', label: 'Immutable Quote', kind: 'output' }
      ]
    },
  },

  'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces': {
    conceptChecks: [
      {
        id: 'lesson-4-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01',
        question:
          'An order service must support card, wallet, and bank-transfer payments without changing its orchestration code when a new payment method is added. Which design best preserves the contract?',
        options: [
          { id: 'a', label: 'A', text: 'Make PaymentService branch on each provider with instanceof checks.' },
          { id: 'b', label: 'B', text: 'Depend on a small PaymentAuthorizer interface and register adapters that implement it.' },
          { id: 'c', label: 'C', text: 'Expose every gateway SDK method on one large interface so all callers share one type.' },
          { id: 'd', label: 'D', text: 'Put provider-specific response translation in the controller before calling the service.' }
        ],
        correctOptionId: 'b',
        explanation:
          'A consumer-shaped PaymentAuthorizer keeps PaymentService focused on the use case. Each adapter translates its provider at the boundary, while dynamic dispatch lets the service work through the same contract when another implementation is registered.',
        incorrectExplanation:
          'Look for the boundary that owns provider-specific behavior. The application service should depend on a capability, not on concrete SDK types or a growing chain of type checks.',
        hint: 'PaymentService → capability contract → provider adapters',
        initialSelectedOption: 'b',
        initialSubmitted: true
      }
    ],
    architecture: {
      id: 'lesson-4-payment-authorization-flow',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — PAYMENT AUTHORIZATION',
      boundaryLabel: 'BOUNDARY ACCEPTED',
      boundaryText:
        'PaymentService depends on authorization capability, not on the infrastructure that provides it.',
      nodes: [
        { id: 'request', label: 'Request', kind: 'input' },
        { id: 'service', label: 'PaymentService', kind: 'service' },
        { id: 'contract', label: 'PaymentAuthorizer', kind: 'boundary', highlighted: true },
        { id: 'card', label: 'CardAuthorizer', kind: 'adapter' },
        { id: 'wallet', label: 'WalletAuthorizer', kind: 'adapter' },
        { id: 'bank', label: 'BankTransferAuthorizer', kind: 'adapter' },
        { id: 'result', label: 'AuthorizationResult', kind: 'output' }
      ]
    },
  }
};

export function getLessonInteractions(courseSlug, moduleSlug, lessonSlug) {
  return lessonInteractions[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonInteractions;
