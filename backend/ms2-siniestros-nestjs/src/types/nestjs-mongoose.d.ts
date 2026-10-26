declare module '@nestjs/mongoose' {
  import { DynamicModule, Type } from '@nestjs/common';
  import { Connection, ConnectOptions } from 'mongoose';

  export interface MongooseModuleOptions extends ConnectOptions {
    uri?: string;
    retryAttempts?: number;
    retryDelay?: number;
    connectionName?: string;
    connectionFactory?: (connection: any, name?: string) => any;
    lazyConnection?: boolean;
    [key: string]: any;
  }

  export interface ModelDefinition {
    name: string;
    schema: any;
    collection?: string;
  }

  export class MongooseModule {
    static forRoot(uri: string, options?: MongooseModuleOptions): DynamicModule;
    static forRootAsync(options: any): DynamicModule;
    static forFeature(models?: ModelDefinition[], connectionName?: string): DynamicModule;
    static forFeatureAsync(factories?: any[], connectionName?: string): DynamicModule;
  }

  export function InjectConnection(connectionName?: string): ParameterDecorator;
  export function InjectModel(modelName: string): ParameterDecorator;
  export function Prop(options?: any): PropertyDecorator;
  export function Schema(options?: any): ClassDecorator;
  export const SchemaFactory: {
    createForClass: (target: any) => any;
  };
}
