// Queue Handler

export async function handleQueue(request, env) {
  const url = new URL(request.url);
  const pathname = url.pathname;

  // Add job to queue
  if (pathname === '/queue/add' && request.method === 'POST') {
    try {
      const body = await request.json();
      const { videoId, options } = body;

      // Add to KV storage (Cloudflare KV)
      const jobId = crypto.randomUUID();
      const job = {
        id: jobId,
        videoId: videoId,
        options: options,
        status: 'pending',
        createdAt: new Date().toISOString()
      };

      // Store in KV (if configured)
      if (env.JOB_QUEUE) {
        await env.JOB_QUEUE.put(`job:${jobId}`, JSON.stringify(job));
      }

      return new Response(JSON.stringify({
        success: true,
        jobId: jobId,
        message: 'Job added to queue'
      }), {
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Failed to add job'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  // Get job status
  if (pathname.startsWith('/queue/status/') && request.method === 'GET') {
    try {
      const jobId = pathname.split('/').pop();
      // Get from KV
      let job = null;
      if (env.JOB_QUEUE) {
        const jobData = await env.JOB_QUEUE.get(`job:${jobId}`);
        if (jobData) {
          job = JSON.parse(jobData);
        }
      }

      if (!job) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Job not found'
        }), {
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      return new Response(JSON.stringify({
        success: true,
        job: job
      }), {
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Failed to get job status'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  // List all jobs
  if (pathname === '/queue/list' && request.method === 'GET') {
    try {
      let jobs = [];
      
      if (env.JOB_QUEUE) {
        const list = await env.JOB_QUEUE.list({ prefix: 'job:' });
        for (const key of list.keys) {
          const jobData = await env.JOB_QUEUE.get(key.name);
          if (jobData) {
            jobs.push(JSON.parse(jobData));
          }        }
      }

      return new Response(JSON.stringify({
        success: true,
        jobs: jobs
      }), {
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Failed to list jobs'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  return new Response('Not Found', { status: 404 });
}
