import { LitElement, nothing } from 'lit';
import { ComponentContext, ComponentApi, type ComponentId } from '@a2ui/web_core/v0_9';
import { A2uiController } from './a2ui-controller.js';
/**
 * A reference to a child component to render. Either a string ID, or an object
 * pairing an ID with an explicit data context path.
 */
type A2uiChildRef = ComponentId | {
    id: ComponentId;
    basePath: string;
};
/**
 * A base class for A2UI Lit elements that manages the A2uiController lifecycle.
 *
 * This element handles the reactive attachment and detachment of the `A2uiController`
 * whenever the component's `context` changes. Subclasses only need to implement
 * `createController` to provide their specific schema-bound controller, and `render`
 * to define the template based on the controller's reactive props.
 *
 * @template Api The specific A2UI component API defining the schema for this element.
 */
export declare abstract class A2uiLitElement<Api extends ComponentApi> extends LitElement {
    accessor context: ComponentContext;
    protected controller: A2uiController<Api>;
    /**
     * Instantiates the unique controller for this element's specific bound API.
     *
     * Subclasses must implement this method to return an `A2uiController` tied to
     * their specific component `Api` definition.
     *
     * @returns A new instance of `A2uiController` matching the component API.
     */
    protected abstract createController(): A2uiController<Api>;
    /**
     * Helper method to render a child A2UI node.
     * Abstracts away the need to manually create a ComponentContext.
     *
     * @param childRef The reference to the child component to render. Either a string ID
     *                 or a reference object containing `{id, basePath}`.
     * @param customPath An explicit data model path to bind the child to. If provided,
     *                   this overrides any path defined in the `childRef` object. If omitted,
     *                   falls back to the `childRef`'s `basePath`, or the current component's path.
     *
     * @returns A Lit template result containing the rendered child component, or `nothing` if the reference is empty.
     */
    protected renderNode(childRef?: A2uiChildRef, customPath?: string): import("lit-html").TemplateResult | typeof nothing;
    /**
     * Reacts to changes in the component's properties.
     *
     * Specifically, when the `context` property changes or is initialized, this method
     * cleans up any existing controller and invokes `createController()` to bind to
     * the new context.
     */
    willUpdate(changedProperties: Map<string, any>): void;
}
export {};
//# sourceMappingURL=a2ui-lit-element.d.ts.map