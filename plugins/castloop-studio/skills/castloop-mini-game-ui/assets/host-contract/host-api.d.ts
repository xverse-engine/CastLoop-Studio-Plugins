/** Protocol 1.1 / package specification 1.2. Deployment and device certification are separate. */
export type Json=null|boolean|number|string|Json[]|{[key:string]:Json};
export type JsonObject={[key:string]:Json};
export type UnlockMethod='free'|'diamonds'|'membership'|'rewarded_ad';
export interface SaveRecord{schemaVersion:number;revision:number;data:JsonObject}
export interface Offer{grantKey:string;kind:'consumable'|'unlock';remaining:number;diamondCost:number;freeUses:number;membership:boolean;rewardedAd:boolean;methods:{method:UnlockMethod;available:boolean}[]}
export interface SessionContext{
  game:{gameId:string;gameVersion:string;protocolVersion:'1.1';miniGameData:JsonObject};
  initialParams:JsonObject;save:SaveRecord|null;offers:Offer[];showRewardedAd:boolean;
  result:'success'|'failure'|'skipped'|null;
  activeReservation:{operationId:string;reservationId:string;grantKey:string}|null;
  pendingOperations:{operationId:string;method:UnlockMethod}[];
  locale?:string;capabilities?:string[];
}
export interface CastloopGameHost{
  call(type:'connect'|'context',payload?:{}):Promise<SessionContext>;
  call(type:'ready',payload?:{}):Promise<{status:'ready'}>;
  call(type:'getOffer',payload:{offerId:string}):Promise<Offer>;
  /** Only the host displays payment choices and creates unlock orders. */
  call(type:'requestUnlock',payload:{offerId:string}):Promise<{status:'granted'|'cancelled';operationId?:string}>;
  call(type:'createOperation',payload:{kind:'consume';key:string}):Promise<{operationId:string}>;
  call(type:'getOperation',payload:{operationId:string}):Promise<{status:string;operationId?:string}>;
  call(type:'loadSave',payload?:{}):Promise<SaveRecord|null>;
  call(type:'saveSnapshot',payload:{schemaVersion:1;expectedRevision:number;data:JsonObject}):Promise<SaveRecord>;
  call(type:'reserveUse',payload:{operationId:string;expectedRevision:number}):Promise<{reservationId:string}>;
  call(type:'commitUse',payload:{reservationId:string;expectedRevision:number;data:JsonObject;resultCode?:'skipped'}):Promise<{status:'committed';save:SaveRecord;result:string|null}>;
  call(type:'cancelUse',payload:{reservationId:string}):Promise<{status:string}>;
  call(type:'submitResult',payload:{resultCode:'success'|'failure'|'skipped'}):Promise<{status:'accepted'}>;
  call(type:'requestExit',payload:{reason:'back'|'story_tree'|'abandon'}):Promise<{status:'accepted'}>;
  onEvent(handler:(event:{type:'pause'|'resume'|'capabilitiesChanged'|'contextChanged'|'destroy';payload?:{reason?:string}})=>void):()=>void;
  destroy():void;
}
