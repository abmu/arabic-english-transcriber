declare module 'recordrtc' {
  const RecordRTC: any;
  export default RecordRTC;

  export class StereoAudioRecorder {
    constructor(stream: MediaStream, options?: any);
  }
}
