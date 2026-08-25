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
    exercise: {
      id: 'lesson-1-quote-service-boundary',
      eyebrow: 'IMPLEMENTATION EXERCISE 01',
      title: 'Design the QuoteService boundary',
      description:
        'Complete the smallest use-case boundary so distance lookup, pricing, immutable results, and duplicate request handling stay separate from the HTTP layer.',
      language: 'JAVA',
      difficulty: 'INTRODUCTORY',
      estimatedMinutes: 15,
      entryFileId: 'quote-service',
      files: [
        {
          id: 'quote-service',
          name: 'QuoteService.java',
          path: 'src/main/java/com/neuralascent/quotes/QuoteService.java',
          editable: true,
          role: 'editable',
          content: `public final class QuoteService {

    private final DistanceProvider distanceProvider;
    private final PricingPolicy pricingPolicy;

    public QuoteService(DistanceProvider distanceProvider,
                        PricingPolicy pricingPolicy) {
        this.distanceProvider = distanceProvider;
        this.pricingPolicy = pricingPolicy;
    }

    public Quote createQuote(QuoteRequest request) {
        // TODO: validate, delegate, and return an immutable quote.
        return null;
    }
}`
        }
      ],
      evidence: [
        { id: 'responsibility', label: 'controller responsibility stays outside pricing', status: 'passed' },
        { id: 'delegation', label: 'distance and pricing are delegated', status: 'passed' },
        { id: 'immutability', label: 'immutable quote is returned', status: 'passed' },
        { id: 'validation', label: 'invalid request state is rejected', status: 'passed' },
        {
          id: 'idempotency',
          label: 'duplicate request ID returns the same quote',
          status: 'failed',
          message: 'A repeated request ID still creates a fresh quote instead of reusing the original application outcome.',
          source: 'QuoteServiceTest.java:96',
          hint: 'Which boundary can remember a request outcome before negotiating a second quote?',
          prompt: 'requestId → ? → immutable Quote'
        }
      ]
    }
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
    exercise: {
      id: 'lesson-4-payment-authorizer-boundary',
      eyebrow: 'IMPLEMENTATION EXERCISE 01',
      title: 'Design the PaymentAuthorizer boundary',
      description:
        'Complete PaymentService so dispatch stays polymorphic, provider responses remain behind adapters, and a new payment method can be registered without editing the service.',
      language: 'JAVA',
      difficulty: 'INTRODUCTORY',
      estimatedMinutes: 15,
      entryFileId: 'payment-service',
      files: [
        {
          id: 'payment-service',
          name: 'PaymentService.java',
          path: 'src/main/java/com/neuralascent/payments/PaymentService.java',
          editable: true,
          role: 'editable',
          content: `public final class PaymentService {

    private final PaymentAuthorizerRegistry registry;

    public PaymentService(PaymentAuthorizerRegistry registry) {
        this.registry = registry;
    }

    public AuthorizationResult authorize(PaymentRequest request) {
        // TODO: validate, resolve the capability,
        // and delegate without branching on adapters.
        return null;
    }
}`
        },
        {
          id: 'payment-authorizer',
          name: 'PaymentAuthorizer.java',
          path: 'src/main/java/com/neuralascent/payments/PaymentAuthorizer.java',
          editable: false,
          role: 'reference',
          content: `public interface PaymentAuthorizer {

    boolean supports(String paymentMethod);

    AuthorizationResult authorize(PaymentRequest request);
}`
        },
        {
          id: 'credit-card-authorizer',
          name: 'CreditCardAuthorizer.java',
          path: 'src/main/java/com/neuralascent/payments/CreditCardAuthorizer.java',
          editable: true,
          role: 'editable',
          content: `public final class CreditCardAuthorizer implements PaymentAuthorizer {

    @Override
    public boolean supports(String paymentMethod) {
        return "CARD".equals(paymentMethod);
    }

    @Override
    public AuthorizationResult authorize(PaymentRequest request) {
        // Provider-specific translation belongs at this boundary.
        return AuthorizationResult.approved();
    }
}`
        },
        {
          id: 'payment-request',
          name: 'PaymentRequest.java',
          path: 'src/main/java/com/neuralascent/payments/PaymentRequest.java',
          editable: false,
          role: 'reference',
          content: `public record PaymentRequest(
        String paymentMethod,
        String requestId,
        long amountInCents) {
}`
        },
        {
          id: 'authorization-result',
          name: 'AuthorizationResult.java',
          path: 'src/main/java/com/neuralascent/payments/AuthorizationResult.java',
          editable: false,
          role: 'reference',
          content: `public record AuthorizationResult(String status) {

    public static AuthorizationResult approved() {
        return new AuthorizationResult("APPROVED");
    }
}`
        },
        {
          id: 'payment-authorizer-registry',
          name: 'PaymentAuthorizerRegistry.java',
          path: 'src/main/java/com/neuralascent/payments/PaymentAuthorizerRegistry.java',
          editable: false,
          role: 'reference',
          content: `public interface PaymentAuthorizerRegistry {

    PaymentAuthorizer resolve(String paymentMethod);
}`
        }
      ],
      evidence: [
        { id: 'contract', label: 'consumer depends on the interface', status: 'passed' },
        { id: 'dispatch', label: 'dynamic dispatch reaches the adapter', status: 'passed' },
        { id: 'translation', label: 'provider response stays behind the boundary', status: 'passed' },
        { id: 'failure', label: 'declined and timeout outcomes are normalized', status: 'passed' },
        {
          id: 'extension',
          label: 'new payment method needs no service branch',
          status: 'failed',
          message: 'Adding CryptoAuthorizer still requires a change inside PaymentService instead of a new registration.',
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
