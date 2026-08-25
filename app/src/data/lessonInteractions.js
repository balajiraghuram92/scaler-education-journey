const lessonInteractions = {
  'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces': {
    conceptChecks: [
      {
        id: 'lesson-4-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01',
        question:
          'An order service must support card, wallet, and bank-transfer payments without changing its orchestration code when a new payment method is added. Which design best preserves the contract?',
        options: [
          {
            id: 'a',
            label: 'A',
            text: 'Make PaymentService branch on each provider with instanceof checks.'
          },
          {
            id: 'b',
            label: 'B',
            text: 'Depend on a small PaymentAuthorizer interface and register adapters that implement it.'
          },
          {
            id: 'c',
            label: 'C',
            text: 'Expose every gateway SDK method on one large interface so all callers share one type.'
          },
          {
            id: 'd',
            label: 'D',
            text: 'Put provider-specific response translation in the controller before calling the service.'
          }
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
    exercise: {
      id: 'lesson-4-payment-authorizer-boundary',
      eyebrow: 'IMPLEMENTATION EXERCISE 01',
      title: 'Design the PaymentAuthorizer boundary',
      description:
        'Complete PaymentService so dispatch stays polymorphic, provider responses remain behind adapters, and a new payment method can be registered without editing the service.',
      language: 'JAVA',
      difficulty: 'INTRODUCTORY',
      estimatedMinutes: 15,
      editableFile: 'PaymentService.java',
      starterCode: `public final class PaymentService {

    private final PaymentAuthorizerRegistry registry;

    public PaymentService(PaymentAuthorizerRegistry registry) {
        this.registry = registry;
    }

    public AuthorizationResult authorize(PaymentRequest request) {
        // TODO: validate the request, resolve the capability,
        // and delegate without branching on concrete adapters.
        return null;
    }
}`,
      evidence: [
        { id: 'contract', label: 'consumer depends on the interface', status: 'passed' },
        { id: 'dispatch', label: 'dynamic dispatch reaches the adapter', status: 'passed' },
        { id: 'translation', label: 'provider response stays behind the boundary', status: 'passed' },
        { id: 'failure', label: 'declined and timeout outcomes are normalized', status: 'passed' },
        {
          id: 'extension',
          label: 'new payment method needs no service branch',
          status: 'failed',
          message:
            'Adding CryptoAuthorizer still requires a change inside PaymentService instead of a new registration.',
          source: 'PaymentServiceTest.java:118',
          hint: 'Which boundary should choose the strategy, and which boundary should translate the gateway response?',
          prompt: 'PaymentMethod → ? → PaymentAuthorizer'
        }
      ]
    }
  }
};

export function getLessonInteractions(courseSlug, moduleSlug, lessonSlug) {
  return lessonInteractions[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonInteractions;
