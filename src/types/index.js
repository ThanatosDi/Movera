/**
   * @param {string} id
   * @param {string} name
   * @param {string} include
   * @param {string} move_to
   * @param {string} src_filename_regex
   * @param {string} dst_filename_regex
   * @param {boolean} enabled
   * @param {string} created_at
   * @param {Array<Log>} logs
   */
export class Task {
  /**
   * @param {object} data The data to create a task from.
   * @param {string} data.id
   * @param {string} data.name
   * @param {string} data.include
   * @param {string} data.move_to
   * @param {string} data.src_filename_regex
   * @param {string} data.dst_filename_regex
   * @param {boolean} data.enabled
   * @param {string} data.created_at
   * @param {Array<Log>} data.logs
   */
  constructor({
    id,
    name,
    include,
    move_to,
    src_filename_regex,
    dst_filename_regex,
    enabled,
    created_at,
    logs
  }) {
    this.id = id
    this.name = name
    this.include = include
    this.move_to = move_to
    this.src_filename_regex = src_filename_regex
    this.dst_filename_regex = dst_filename_regex
    this.enabled = enabled
    this.created_at = new Date(created_at)
    this.logs = logs || []
  }

  /**
   * Get a simple object representation of the task.
   * @returns {object}
   */
  toObject() {
    return {
      id: this.id,
      name: this.name,
      include: this.include,
      move_to: this.move_to,
      src_filename_regex: this.src_filename_regex,
      dst_filename_regex: this.dst_filename_regex,
      enabled: this.enabled,
      created_at: this.created_at.toISOString(),
      logs: this.logs,
    }
  }
}



/**
 * Represents a Log.
 */
export class Log {
  /**
    * @param {object} data The data to create a log from.
    * @param {number|string} data.id
    * @param {string} data.task_id
    * @param {string} data.level
    * @param {string} data.message
    * @param {Date} data.timestamp
    */
  constructor({ id, task_id, level, message, timestamp }) {
    this.id = id
    this.task_id = task_id
    this.level = level
    this.message = message
    this.timestamp = new Date(timestamp)
  }

  /**
   * Get a simple object representation of the task.
   * @returns {object}
   */
  toObject() {
    return {
      id: this.id,
      task_id: this.task_id,
      level: this.level,
      message: this.message,
      timestamp: this.timestamp,
    }
  }
}